package jp.ac.tsukuba.s.s2020602.belief;

import com.github.jfasttext.JFastText;
import jp.ac.tsukuba.s.s2020602.utils.BenriFunctions;
import jp.ac.tsukuba.s.s2020602.utils.DebugPrint;
import jp.ac.tsukuba.s.s2020602.utils.Stopwatch;
import org.aiwolf.common.data.Agent;
import org.aiwolf.common.data.Role;
import org.aiwolf.common.data.Team;
import org.aiwolf.common.net.GameSetting;

import java.util.*;
import java.util.stream.Collectors;

/** 信念 */
public class Brain implements DebugPrint, BenriFunctions {
    
    /** 自分以外の生存エージェント（追放・襲撃されたらremoveする。） */
    private final Set<Agent> aliveOthers;
    
    /**
     * 役職推定の対象となる役職（自分以外のエージェントの役職としてあり得るものすべて。
     * ただし，自分が人狼であるとき，自分以外にも人狼がいたとしても，人狼は含めない。）
     */
    private final Set<Role> estimateTargetRoles;
    
    /** 可能世界を区別するために使う役職 */
    private final List<Role> watchingTargetRoles;
    
    /** 主人公を含むすべてのエージェント（襲撃・追放されても削除されない）（eventListMapのkeyになるので必要。） */
    final Set<Agent> allAgents;
    
    /**
     * belief の keySet になる（可能性のある）RoleProfile の集合。watchingTargetRoles（と myRole）によって決まる。
     * 5人村ではこれをそのまま keySet にするが，15人村ではここからさらに絞る。
     */
    private Set<RoleProfile> roleProfileSet;
    
    /** 信念。役職プロファイル -> 確からしさ の Map */
    public Map<RoleProfile, Double> belief;
    
    /** 役職の推定結果。(エージェント, 役職) -> 確からしさ */
    private AgentRoleProbabilityMatrix arpm;
    
    /** 各人目線でのイベントリスト */
    private final Map<Agent, EventList> eventListMap;
    
    /** 5人村に存在する役職。最初は5個要素があるが，5人村のゲームでは自分の役職を削除したうえで使用する。 */
    private ArrayList<Role> roleList5 = new ArrayList<Role>(Arrays.asList(
            Role.WEREWOLF, Role.POSSESSED, Role.SEER, Role.VILLAGER, Role.VILLAGER));
    
    /** 自分以外のエージェントのインデックス（1〜5・1〜15）のリスト */
    private List<Integer> otherAgentIndex;
    
    /** 自分 */
    Agent me;
    
    /** 自分の役職 */
    Role myRole;
    
    /** 村の人数 */
    int villageSize;
    
    /** 自分の役職についての記述（eventListの文字列の最初に加わる。） */
    String myRoleDescription;
    
    /** SKIP・OVER をイベントリストに含めるかどうか（trueならば含める） */
    boolean includeSkipOver = true;
    
    /** 各学習済みモデルをロードしたJFsstTextのインスタンスの集まり */
    LoadedModelMap lmm = null;
    
    /** ゲーム設定 */
    GameSetting gameSetting;
    
    /**
     * 可能世界の定義域（？）になるエージェントの集合。
     * （自分以外のすべてのエージェント。ただし自分が人狼のときは，「(人狼であるエージェント) 以外のエージェント」になる。）
     */
    List<Agent> beliefDomain;
    
    /** 「61.71％：(4:狼, 5:狼, 7:狼)」のようなものを表示するかどうか */
    boolean printRoleProfileProb = false;
    
    /** 自称占い師のリスト */
    public Set<Agent> declaredSeers = new HashSet<>();
    
    ////////////////////////////////////////////////////////////////////////////////////////////////////
    
    @Override
    public String toString() {
        String str = "各人のEventList: " + eventListMap.toString();
        return str;
    }
    
    ////////////////////////////////////////////////////////////////////////////////////////////////////
    
    /** コンストラクタ */
    public Brain(Set<Agent> allOthers, Set<Role> estimateTargetRoles, Role myRole, Set<Agent> allAgents, Agent me, LoadedModelMap lmm, Collection<Role> watchingTargetRoles, GameSetting gameSetting, Set<Agent> beliefDomain, Set<Agent> declaredSeers) {
        this.gameSetting = gameSetting;
        
        this.lmm = lmm;
        
        this.me = me;
        belief = new HashMap<>();
        
        this.aliveOthers = new HashSet<>(allOthers);
        this.estimateTargetRoles = new HashSet<>(estimateTargetRoles);
        arpm = new AgentRoleProbabilityMatrix(allOthers, estimateTargetRoles);
        
        this.allAgents = new HashSet<>(allAgents);
        villageSize = allAgents.size();
        
        eventListMap = new HashMap<>();
        // eventListMapの初期化：自分を含む各エージェントについてリストを作成。
        for (Agent agent : this.allAgents) {
            EventList eventList = new EventList(agent);
            eventListMap.put(agent, eventList);
        }
        
        this.myRole = myRole;
        myRoleDescription = "";
        
        this.watchingTargetRoles = new ArrayList<>(watchingTargetRoles);
        
        // otherAgentIndex = 自分以外のエージェントのインデックスのリスト。
        otherAgentIndex = new ArrayList<>();
        for (int i = 1; i <= villageSize; i++) {
            otherAgentIndex.add(i);
        }
        otherAgentIndex.remove(me.getAgentIdx() - 1);
        
        this.beliefDomain = new ArrayList<>(beliefDomain);
        
        roleProfileSet = new HashSet<>();
        makeRoleProfileSet();
        
        this.declaredSeers = declaredSeers;
    }
    
    ////////////////////////////////////////////////////////////////////////////////////////////////////
    ///// public メソッド
    ////////////////////////////////////////////////////////////////////////////////////////////////////
    
    /** 最新の情報で役職推定を行います。 */
    public void estimate() {
        Stopwatch sw1 = new Stopwatch();
        sw1.start();
        
        // 主人公の視点で，各targetRoleのためのモデルをロードして，予測した結果を arpm に格納する。
        
        // 現時点でのイベントリスト
        String eventList = myRoleDescription + eventListMap.get(me).getEventList();
        
        for (Role targetRole : estimateTargetRoles) {
            String text = eventList + " Who is_a " + targetRole + "?";
            List<JFastText.ProbLabel> probLabelList = lmm.getModel(villageSize, myRole, targetRole, declaredSeers.size()).predictProba(text, villageSize - 1);
            if (Objects.isNull(probLabelList)) {
                log("probLabelList was NULL!");
                continue;
            }
            for (JFastText.ProbLabel probLabel : probLabelList) {
                arpm.setAgentRoleProbability(
                        Agent.getAgent(eventListMap.get(me).decodeAgentNumber(Integer.parseInt(probLabel.label.substring(15, 17)))),
                        targetRole, probLabel.logProb);
            }
            
            arpm.setProbSumToOneForEachAgent();
        }
        
        // 役職推定結果の確認
        // log("Role Estimation Result: " + arpm);
        
        sw1.stop();
    }
    
    /**
     * 信念（belief）を更新します。具体的には，直前におこなわれた estimate() の結果たる arpm をもとに，
     * 各 RoleProfile に確からしさを割り振ります。
     */
    public void updateBelief() {
        if (villageSize == 5) {
            // 5人村
            for (RoleProfile rp : roleProfileSet) {
                double prob = 1.0;
                for (Agent agent : rp.getAgentSet()) {
                    if (myRole == Role.VILLAGER && rp.getRole(agent) == Role.VILLAGER) {
                        continue;
                    }
                    prob *= arpm.getAgentRoleProbability(agent, rp.getRole(agent));
                }
                belief.put(rp, prob);
            }
            
        } else {
            // 15人村
            for (RoleProfile rp : roleProfileSet) {
                double prob = 1.0;
                for (Agent agent : rp.getAgentSet()) {
                    prob *= arpm.getAgentRoleProbability(agent, rp.getRole(agent));
                }
                belief.put(rp, prob);
            }
        }
        // log(belief.toString());
        
        // 確率の昇順でソート
        belief = belief.entrySet()
                .stream()
                .sorted(Map.Entry.<RoleProfile, Double>comparingByValue().reversed())
                .collect(Collectors.toMap(
                        Map.Entry::getKey, Map.Entry::getValue,
                        (e1, e2) -> e1, LinkedHashMap::new));
        
        // 「61.71％：(4:狼, 5:狼, 7:狼)」のようなものを表示する
        if (printRoleProfileProb) {
            for (Map.Entry<RoleProfile, Double> entry : belief.entrySet()) {
                simpleLog(String.format("%.2f", entry.getValue() * 100) + "%: " + entry.getKey().toString());
            }
            log("");
        }
    }
    
    
    /** （自分から見て）ピンポイントで1つの役職に関する推定を行うときに使用します， */
    public Agent getPinpointEstimation(Role targetRole) {
        Agent returnAgent = null;
        String text = myRoleDescription + eventListMap.get(me).getEventList() + " Who is_a " + targetRole + "?";
        JFastText.ProbLabel probLabel = lmm.getModel(villageSize, myRole, targetRole, declaredSeers.size()).predictProba(text);
        returnAgent = Agent.getAgent(eventListMap.get(me).decodeAgentNumber(Integer.parseInt(probLabel.label.substring(15, 17))));
        log("Prob(" + returnAgent.toString() + ":" + targetRole + ") = " + (probLabel.logProb * 100) + " %");
        return returnAgent;
    }
    
    /** ownRoleであるその人から見て，いちばんその役職っぽい人を返します。 */
    public Agent getPinpointEstimation(Agent estimator, Role ownRole, Role targetRole) {
        Agent returnAgent = null;
        String text = eventListMap.get(estimator).getEventList() + " Who is_a " + targetRole + "?";
        JFastText.ProbLabel probLabel = lmm.getModel(villageSize, ownRole, targetRole, declaredSeers.size()).predictProba(text);
        returnAgent = Agent.getAgent(eventListMap.get(estimator).decodeAgentNumber(Integer.parseInt(probLabel.label.substring(15, 17))));
        log("Prob(" + returnAgent.toString() + ":" + targetRole + ") = " + (probLabel.logProb * 100) + " %");
        return returnAgent;
    }
    
    /** 主人公が myTalkContent と言ったときの，役職 ownRole たる votingAgent の投票先（targetRole を狙うものとする）を予測して返します。 */
    public Agent getVotedAgent_addingMyTalk(Agent votingAgent, Role ownRole, Role targetRole, String myTalkContent) {
        String text = eventListMap.get(votingAgent).getEventList_withTempTalk(me, myTalkContent) + " Who is_a " + targetRole + "?";
        List<JFastText.ProbLabel> probLabels = lmm.getModel(villageSize, ownRole, targetRole, declaredSeers.size()).predictProba(text, villageSize - 1);
        for (JFastText.ProbLabel probLabel : probLabels) {
            Agent watchedAgent = Agent.getAgent(eventListMap.get(votingAgent).decodeAgentNumber(Integer.parseInt(probLabel.label.substring(15, 17))));
            if ((aliveOthers.contains(watchedAgent) || watchedAgent == me) && watchedAgent != votingAgent) {
                // 生存していて，かつ，votingAgent とは別人であることが必要
                return watchedAgent;
            }
        }
        // たぶんここに来ることはない…。
        return me;
    }
    
    /** <b>生存しているエージェントのうち</b>，（自分から見て）いちばんその役職っぽい人を返します。 */
    public Agent getPinpointEstimation_alive(Role targetRole) {
        // 探している役職が 人狼 であって，1人以上の人狼が判明しているときは，その人たちの中から生存している人を返す。
        if (targetRole == Role.WEREWOLF && !arpm.blackList.isEmpty()) {
            for (Agent blackAgent : arpm.blackList) {
                if (aliveOthers.contains(blackAgent)) {
                    return blackAgent;
                }
            }
        }
        
        String text = myRoleDescription + eventListMap.get(me).getEventList() + " Who is_a " + targetRole + "?";
        List<JFastText.ProbLabel> probLabels = lmm.getModel(villageSize, myRole, targetRole, declaredSeers.size()).predictProba(text, villageSize - 1);
        for (JFastText.ProbLabel probLabel : probLabels) {
            Agent watchedAgent = Agent.getAgent(eventListMap.get(me).decodeAgentNumber(Integer.parseInt(probLabel.label.substring(15, 17))));
            if (aliveOthers.contains(watchedAgent)) {
                simpleLog("Prob(" + watchedAgent.toString() + ":" + toKanji(targetRole) + ") = " + (probLabel.logProb * 100) + " %");
                return watchedAgent;
            }
        }
        // たぶんここに来ることはない…。
        return me;
    }
    
    /** <b>agentSet として与えられたエージェントたちのうち</b>，（自分から見て）いちばんその役職っぽい人を返します。 */
    public Agent getPinpointEstimation_inSet(Role targetRole, Set<Agent> agentSet) {
        // 探している役職が 人狼 であって，1人以上の人狼が判明しているときは，その人たちの中から生存している人を返す。
        if (targetRole == Role.WEREWOLF && !arpm.blackList.isEmpty()) {
            for (Agent blackAgent : arpm.blackList) {
                if (agentSet.contains(blackAgent)) {
                    return blackAgent;
                }
            }
        }
        
        String text = myRoleDescription + eventListMap.get(me).getEventList() + " Who is_a " + targetRole + "?";
        List<JFastText.ProbLabel> probLabels = lmm.getModel(villageSize, myRole, targetRole, declaredSeers.size()).predictProba(text, villageSize - 1);
        for (JFastText.ProbLabel probLabel : probLabels) {
            Agent watchedAgent = Agent.getAgent(eventListMap.get(me).decodeAgentNumber(Integer.parseInt(probLabel.label.substring(15, 17))));
            if (agentSet.contains(watchedAgent)) {
                simpleLog("Prob(" + watchedAgent.toString() + ":" + toKanji(targetRole) + ") = " + (probLabel.logProb * 100) + " %");
                return watchedAgent;
            }
        }
        // たぶんここに来ることはない…。
        return me;
    }
    
    
    /** 与えられたエージェントが Agent[01] になった視点でのイベントリストを返します。 */
    public EventList getEventList(Agent agent) {
        return eventListMap.get(agent);
    }
    
    ////////////////////////////////////////////////////////////////////////////////////////////////////
    ///// private メソッド
    ////////////////////////////////////////////////////////////////////////////////////////////////////
    
    /** watchingTargetRoles（と myRole）によって，belief の keySet になる（可能性のある）RoleProfile の集合を作成する。 */
    private void makeRoleProfileSet() {
        simpleLog("[makeRoleProfileSet]");
        if (villageSize == 5) { // 5人村
            roleList5.remove(myRole);
            simpleLog(roleList5.toString());
            
            List<List<Role>> lists = BenriFunctions.permutationsList(roleList5.size(), roleList5);
            simpleLog(lists.toString());
            
            for (List<Role> e : lists) {
                RoleProfile rp = new RoleProfile();
                int i = 0;
                for (int agentIdx : otherAgentIndex) {
                    rp.put(Agent.getAgent(agentIdx), e.get(i));
                    i++;
                }
                roleProfileSet.add(rp);
            }
            
        } else { // 15人村
            // watchingTargetRoles の人数を数える
            int watchingAgentsNum = 0;
            for (Role watchingTargetRole : watchingTargetRoles) {
                watchingAgentsNum += gameSetting.getRoleNum(watchingTargetRole);
            }
            
            // Perm(14, r)，あるいは Perm(12, r) のエージェント集合を用意。（Perm：permutation）
            if (watchingTargetRoles.size() == 1) { // たぶん：人狼。組み合わせの数は Comb(14, 3)。（Comb：combination）
                if (watchingAgentsNum != 3) {
                    log("【困ります！】 watchingTargetRoles の大きさが 1 だから人狼（3 人）だと思ったのに！！");
                }
                // 以下，3人のときだけ考えます。
                
                // watchingTargetRoles の要素は 1 個だけなので，これで取得できる。
                Role watchingTargetRole = watchingTargetRoles.get(0);
                
                for (int i = 0; i < beliefDomain.size(); i++) {
                    for (int j = i + 1; j < beliefDomain.size(); j++) {
                        for (int k = j + 1; k < beliefDomain.size(); k++) {
                            RoleProfile rp = new RoleProfile();
                            rp.put(beliefDomain.get(i), watchingTargetRole);
                            rp.put(beliefDomain.get(j), watchingTargetRole);
                            rp.put(beliefDomain.get(k), watchingTargetRole);
                            roleProfileSet.add(rp);
                        }
                    }
                }
            } else { // たぶん：占い師と狩人。順列 Perm(12, 2)
                // デバッグ
                if (watchingTargetRoles.size() == 0) {
                    log("【おかしい！】 watchingTargetRoles の大きさが 0 です！");
                }
                if (watchingTargetRoles.size() > 2) {
                    log("【おかしい！】 watchingTargetRoles の大きさが 2 より大きいです！");
                }
                if (watchingTargetRoles.size() == 2) {
                    // watchingTargetRoles.size() == 2 のときだけ考えることにします。
                    
                    for (Agent agent1 : beliefDomain) {
                        for (Agent agent2 : beliefDomain) {
                            if (agent1 == agent2) {
                                continue;
                            }
                            RoleProfile rp = new RoleProfile();
                            rp.put(agent1, watchingTargetRoles.get(0));
                            rp.put(agent2, watchingTargetRoles.get(1));
                            roleProfileSet.add(rp);
                        }
                    }
                }
            }
        }
    }
    
    ////////////////////////////////////////////////////////////////////////////////////////////////////
    //////////     EventList を構成するためのメソッド
    ////////////////////////////////////////////////////////////////////////////////////////////////////
    
    /**
     * 自分の役職について myRoleDescription に記入する。
     * myRoleDescription は，自分目線の役職推定のときのみ，イベントリストの先頭に追加される。
     * 自分が15人村の人狼の場合は，3人分追加される。
     */
    public void putMyRole(Agent agent, Role role) {
        myRoleDescription = myRoleDescription + " " + eventListMap.get(me).agentString(agent) + " is_a " + role.toString() + ".";
        // log("myRoleDescription: " + myRoleDescription);
        // log("eventListMap.get(me): " + eventListMap.get(me));
    }
    
    /**
     * 役職が明らかになった人について「Agent[xx] is_a WEREWOLF.」などと記載。
     * 占い師や霊媒師が黒判定を出したときに使うことを想定している。
     */
    public void addObviousRole(Agent agent, Role role) {
        // 占いや霊媒の結果は me にしか分からないので，me の eventList にのみ記入する。
        eventListMap.get(me).addObviousRole(agent, role);
        log("addObviousRole: " + agent.toString() + " is " + role);
        
        arpm.grayList.remove(agent);
        if (role.getTeam() == Team.WEREWOLF) {
            arpm.blackList.add(agent);
            log("Add " + agent + " to BlackList.");
        } else {
            arpm.whiteList.add(agent);
            log("Add " + agent + " to WhiteList.");
        }
    }
    
    /**
     * 「なんらかの役職でないこと」が明らかになった人について「Agent[xx] is_not_a WEREWOLF.」などと記載。
     * 占い師や霊媒師が白判定を出したときに使うことを想定している。
     */
    public void addObviousRole_not(Agent agent, Role role) {
        // 占いや霊媒の結果は me にしか分からないので，me の eventList にのみ記入する。
        eventListMap.get(me).addObviousRole_not(agent, role);
        log("addObviousRole_not: " + agent.toString() + " isn't " + role);
        
        if (role.getTeam() == Team.WEREWOLF) {
            arpm.grayList.remove(agent);
            arpm.whiteList.add(agent);
            log("Add " + agent + " to WhiteList");
        }
    }
    
    public void addTalk(Agent talker, String text) {
        if (!includeSkipOver && (text.equals("Over") || text.equals("Skip"))) {
            // Skip と Over を含めない設定になっているときは，Skip と Over を無視する。
            return;
        } else {
            for (Map.Entry<Agent, EventList> entry : eventListMap.entrySet()) {
                entry.getValue().addTalk(talker, text);
            }
            // log("addTalk: " + talker.toString() + "'" + text + "'");
        }
    }
    
    public void addVote(Agent votingAgent, Agent votedAgent) {
        for (Map.Entry<Agent, EventList> entry : eventListMap.entrySet()) {
            entry.getValue().addVote(votingAgent, votedAgent);
        }
    }
    
    public void addRevote() {
        for (Map.Entry<Agent, EventList> entry : eventListMap.entrySet()) {
            entry.getValue().addRevote();
        }
    }
    
    public void addExecution(Agent executedAgent) {
        for (Map.Entry<Agent, EventList> entry : eventListMap.entrySet()) {
            entry.getValue().addExecution(executedAgent);
        }
        aliveOthers.remove(executedAgent);
    }
    
    public void addAttack(Agent attackedAgent) {
        for (Map.Entry<Agent, EventList> entry : eventListMap.entrySet()) {
            entry.getValue().addAttack(attackedAgent);
        }
        aliveOthers.remove(attackedAgent);
        
        // ARPM側のカラーリストの更新
        arpm.grayList.remove(attackedAgent);
        arpm.whiteList.add(attackedAgent);
        log("Add " + attackedAgent + " to WhiteList.");
    }
    
    public void addNewDay(int day) {
        for (Map.Entry<Agent, EventList> entry : eventListMap.entrySet()) {
            entry.getValue().addNewDay(day);
        }
    }
    
}
