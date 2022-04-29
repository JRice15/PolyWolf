package jp.ac.tsukuba.s.s2020602.roles;

import jp.ac.tsukuba.s.s2020602.belief.Brain;
import jp.ac.tsukuba.s.s2020602.belief.LoadedModelMap;
import jp.ac.tsukuba.s.s2020602.belief.RoleProfile;
import jp.ac.tsukuba.s.s2020602.utils.BenriFunctions;
import jp.ac.tsukuba.s.s2020602.utils.DebugPrint;
import org.aiwolf.client.lib.*;
import org.aiwolf.common.data.*;
import org.aiwolf.common.net.GameInfo;
import org.aiwolf.common.net.GameSetting;

import java.util.*;

/**
 * 一部，Sample エージェントのプログラム内のメソッドを利用させていただいております。
 */
public abstract class SashimiBasePlayer implements Player, DebugPrint, BenriFunctions {
    
    /** 調べる世界の個数の上限。デフォルト値は12（5人村で，自分が村人の時を想定）。 */
    int worldCountLimit = 12;
    
    /** 〔15人村のときの〕調べる世界の個数の上限 */
    int worldCountLimit_15 = 5;
    
    /** 村人陣営かどうか（村人陣営ならば1，人狼陣営ならば-1）（利得の計算に用いる。）（各役職のinitializeメソッドで値を決定する。） */
    int isVillagerTeam;
    
    /** 最新のゲーム情報 */
    GameInfo currentGameInfo;
    
    /** プレイヤーの人数 */
    int villageSize;
    
    /** 主人公の脳の中（？） */
    Brain brain;
    
    /** 主人公以外のエージェント（追放・襲撃されてもそのまま）（旧名称：targetAgents） */
    Set<Agent> allOthers;
    
    /**
     * 可能世界の定義域（？）になるエージェントの集合。（自分以外のすべてのエージェント。
     * ただし自分が人狼のときは，「(人狼であるエージェントたち) 以外のエージェント」とする。）
     */
    Set<Agent> beliefDomain;
    
    /**
     * 役職推定の対象となる役職（自分以外のエージェントの役職としてあり得るものすべて。
     * ただし，自分が人狼であるとき，自分以外にも人狼がいたとしても，人狼は含めない。）
     */
    Set<Role> estimateTargetRoles;
    
    /** 投票のときに狙う（単一の）役職 */
    Role voteTargetRole;
    
    /** 可能世界を区別するために使う役職（brain.beliefのkeySet的な？） */
    List<Role> watchingTargetRoles;
    
    /** 主人公を含むすべてのエージェント（襲撃・追放されても削除されない） */
    Set<Agent> allAgents;
    
    /** このエージェント（このプログラム内では「主人公」と呼ぶことがあります。） */
    Agent me;
    
    /** 自分（主人公）の（本当の）役職 */
    Role myRole;
    
    /** 現在の日付 */
    int day;
    
    /** talk() のターン：その日の何ターン目かを示す。 */
    int talkTurn;
    
    /** GameInfo.talkList の読み込みのヘッド */
    int talkListHead;
    
    /** 発言用待ち行列。dayStart() において clear する。 */
    Deque<Content> talkQueue = new LinkedList<>();
    
    /** 自分以外の生存エージェント（initialize()で初期化。executedAgentsとkilledAgentsの更新時に更新。） */
    List<Agent> aliveOthers;
    
    /** 追放されたエージェント（initialize()で初期化。dayStart()とupdate()で更新。） */
    List<Agent> executedAgents = new ArrayList<>();
    
    /** （人狼によって）殺されたエージェント（initialize()で初期化。dayStart()で更新。） */
    List<Agent> killedAgents = new ArrayList<>();
    
    /**
     * （主人公を含む）全員のカミングアウト状況。
     * TODO：正しく更新されていない可能性がある。
     */
    Map<Agent, Role> comingoutMap = new HashMap<>();
    
    /** 発言の選択肢を収める集合 */
    Set<Content> talkChoices = new HashSet<>();
    
    /** 各学習済みモデルをロードしたJFsstTextのインスタンスの集まり */
    LoadedModelMap lmm = null;
    
    /** 再投票かどうか（再投票のときtrue） */
    boolean isRevote;
    
    /** ホワイトリスト（役職が人狼ではないと判明した人たち） */
    Set<Agent> whiteList;
    
    /** ブラックリスト（役職が人狼であると判明した人たち） */
    Set<Agent> blackList;
    
    /** グレーリスト（役職が人狼であるとも人狼でないとも判明していない人たち） */
    Set<Agent> grayList;
    
    /** 自称占い師のリスト */
    public Set<Agent> declaredSeers;
    
    /** 占い師をCOする必要があるとき true になるフラグ */
    protected boolean needComingoutSeer;
    
    /** 直前に投票宣言した対象のエージェント */
    Agent declaredVoteCandidate;
    
    /** ゲーム設定 */
    GameSetting gameSetting;
    
    // ---------------------------------------------------------------------
    // ---------------------------------------------------------------------
    
    /** 空のコンストラクタ */
    public SashimiBasePlayer() {
    }
    
    // ---------------------------------------------------------------------
    // ---------------------------------------------------------------------
    
    @Override
    public String getName() {
        return "SashimiBasePlayer";
    }
    
    @Override
    public void initialize(GameInfo gameInfo, GameSetting gameSetting) {
        // log("getExistingRoles: " + gameInfo.getExistingRoles());
        
        currentGameInfo = gameInfo;
        
        me = currentGameInfo.getAgent();
        villageSize = gameSetting.getPlayerNum();
        myRole = currentGameInfo.getRole();
        
        if (villageSize > 5) {
            worldCountLimit = worldCountLimit_15;
        }
        
        // 各値の初期化
        day = -1; // 日付
        allAgents = new HashSet<>(currentGameInfo.getAgentList());
        aliveOthers = new ArrayList<>(currentGameInfo.getAliveAgentList()); // 自分以外の生存エージェント
        aliveOthers.remove(me); // 「自分以外の」にする
        allOthers = new HashSet<>(aliveOthers);
        
        
        executedAgents.clear(); // 追放されたエージェント
        killedAgents.clear(); // 襲撃されたエージェントのリスト
        comingoutMap.clear(); // （主人公を含む）全員のカミングアウト状況
        
        setVoteTargetRole();
        
        this.estimateTargetRoles = new HashSet<>(currentGameInfo.getExistingRoles());
        if (myRole != Role.VILLAGER) {
            // 自分が VILLAGER でなければ，estimateTargetRoles に myRole を含めない。
            estimateTargetRoles.remove(myRole);
        }
        // log("My Role: " + myRole + ", Roles Considered: " + estimateTargetRoles);
        
        watchingTargetRoles = new ArrayList<>();
        setWatchingTargetRoles();
        
        beliefDomain = new HashSet<>(allOthers);
        // 15人村で，主人公が人狼の場合は，仲間の人狼を beliefDomain から除く。
        if (villageSize > 5 && myRole == Role.WEREWOLF) {
            for (Map.Entry<Agent, Role> entry : gameInfo.getRoleMap().entrySet()) {
                if (entry.getValue() == Role.WEREWOLF && entry.getKey() != me) {
                    beliefDomain.remove(entry.getKey());
                }
            }
        }
        
        declaredSeers = new HashSet<>();
        
        brain = new Brain(allOthers, estimateTargetRoles, myRole, allAgents, me, lmm, watchingTargetRoles, gameSetting, beliefDomain, declaredSeers);
        // log("brain: " + brain);
        
        for (Map.Entry<Agent, Role> entry : currentGameInfo.getRoleMap().entrySet()) {
            // eventList.addObviousRole(entry.getKey(), entry.getValue());
            brain.putMyRole(entry.getKey(), entry.getValue());
        }
        
        // 各種カラーリストの初期化
        whiteList = new HashSet<>();
        blackList = new HashSet<>();
        grayList = new HashSet<>(aliveOthers);
        // grayList は，基本的には最初は aliveOthers であるが，15 人村の人狼にとっては，(aliveOthers - ほかの人狼) となる。
        if (villageSize > 5 && myRole == Role.WEREWOLF) {
            for (Map.Entry<Agent, Role> entry : currentGameInfo.getRoleMap().entrySet()) {
                if (entry.getValue() == Role.WEREWOLF) {
                    grayList.remove(entry.getKey());
                }
            }
        }
        
        needComingoutSeer = false;
        
        declaredVoteCandidate = null;
        
        this.gameSetting = gameSetting;
    }
    
    /** 可能世界を区別するために使う役職を決める。 */
    abstract void setWatchingTargetRoles();
    
    /** voteTargetRole（投票のときに狙う（単一の）役職）を決める。 */
    abstract void setVoteTargetRole();
    
    @Override
    public void update(GameInfo gameInfo) {
        // まず，gameInfoの更新
        currentGameInfo = gameInfo;
        
        // もし自分が生存していなかったら，何もせずリターンする。
        if (!currentGameInfo.getAliveAgentList().contains(me)) {
            return;
        }
        
        // 日付変更の確認
        // 一日の最初の呼び出しは dayStart() の前なので，何もしない
        if (currentGameInfo.getDay() == day + 1) {
            day = currentGameInfo.getDay();
            return;
        }
        
        // 以下，各日の2回目以降の呼び出しにおける処理
        
        // 夜限定：追放されたエージェントを登録
        addExecutedAgent(currentGameInfo.getLatestExecutedAgent());
        
        // 発言を読み取る
        for (int i = talkListHead; i < currentGameInfo.getTalkList().size(); i++) {
            Talk talk = currentGameInfo.getTalkList().get(i);
            Agent talker = talk.getAgent();
            brain.addTalk(talker, talk.getText());
            
            // 自称占い師を declaredSeers に追加するための部分開始。
            Content content = new Content(talk.getText());
            // subjectがUNSPECの場合は発話者に入れ替える
            if (content.getSubject() == Content.UNSPEC) {
                content = replaceSubject(content, talker);
            }
            parseSentence(content);
            // 自称占い師を declaredSeers に追加するための部分終了。
        }
        talkListHead = currentGameInfo.getTalkList().size();
        
        // 再投票前の update における処理
        if (isRevote) { // 再投票のとき。
            // さきほどの投票の結果をイベントリストに追加。currentGameInfo.getLatestVoteList() を使用。
            for (Vote aVote : currentGameInfo.getLatestVoteList()) {
                brain.addVote(aVote.getAgent(), aVote.getTarget());
            }
            // 「再投票が始まるよ」の旨，イベントリストに追加。
            brain.addRevote();
        }
        
        // ここで役職推定してしまう
        brain.estimate();
        brain.updateBelief();
    }
    
    @Override
    public void dayStart() {
        // もし自分が生存していなかったら，何もせずリターンする。
        if (!currentGameInfo.getAliveAgentList().contains(me)) {
            return;
        }
        
        // イベントリストに日付を記入。
        brain.addNewDay(day);
        
        // 各種処理
        talkTurn = -1;
        talkListHead = 0;
        talkQueue.clear();
        isRevote = false;
        
        // 前日に追放されたエージェントを登録
        addExecutedAgent(currentGameInfo.getExecutedAgent());
        
        // 昨夜死亡した（襲撃された）エージェントを登録
        if (!currentGameInfo.getLastDeadAgentList().isEmpty()) {
            addKilledAgent(currentGameInfo.getLastDeadAgentList().get(0));
        }
        
        declaredVoteCandidate = null;
    }
    
    // ---------------------------------------------------------------------
    
    /** 追放されたエージェントを aliveOthers から削除し，executedAgents に登録する */
    void addExecutedAgent(Agent executedAgent) {
        if (executedAgent != null) {
            // 投票結果をイベントリストに追加。currentGameInfo.getVoteList() を使用。
            for (Vote aVote : currentGameInfo.getVoteList()) {
                brain.addVote(aVote.getAgent(), aVote.getTarget());
            }
            
            aliveOthers.remove(executedAgent);
            if (!executedAgents.contains(executedAgent)) {
                executedAgents.add(executedAgent);
                brain.addExecution(executedAgent);
            }
        }
    }
    
    /** 襲撃されたエージェントを aliveOthers から削除し，killedAgents に登録する */
    void addKilledAgent(Agent killedAgent) {
        if (killedAgent != null) {
            aliveOthers.remove(killedAgent);
            if (!killedAgents.contains(killedAgent)) {
                killedAgents.add(killedAgent);
                brain.addAttack(killedAgent);
                
                // Player側のカラーリストの更新
                grayList.remove(killedAgent);
                whiteList.add(killedAgent);
            }
        }
    }
    
    // ---------------------------------------------------------------------
    
    /** talkChoices を更新します。各役職のクラスで実装します。 */
    abstract void updateTalkChoices();
    
    @Override
    public String talk() {
        long start_time = System.currentTimeMillis();
        talkTurn++; // 例：各日の最初の呼び出しで，-1 から 0 になる。（毎日，dayStart() で -1 にリセットしている。）
        
        simpleLog("talk of the Turn " + talkTurn + " of the Day " + day);
        
        if ((day == 1 && talkTurn < 1 && !needComingoutSeer)) {
            // 1日目の最初は，なにもヒントがないので，ランダムに対象を決めて VOTE 発言する。
            Agent targetAgent = randomSelect(aliveOthers);
            if (Objects.isNull(targetAgent)) {
                return Content.SKIP.toString();
            } else {
                String talkContent = voteContent(me, targetAgent).toString();
                log("Random at the 1st turn:" + talkContent);
                return talkContent;
            }
        } else {
            // 可能な発言の選択肢を集める。
            updateTalkChoices();
            // log("talkChoices: " + talkChoices);
            
            // talkChoices が 0個になることがあるらしい
            if (talkChoices.isEmpty()) {
                return Content.SKIP.getText();
            }
            
            // 期待利得計算済みの発言内容候補を格納しておくMap
            Map<Content, Double> expectedPayoff = new HashMap<>();
            
            int computed_talk_choice_count = 0;
            simpleLog("[Computing EU (expected utility)]");
            simpleLog("Number of talkChoices: " + talkChoices.size());
            
            // 自分の投票先は，世界によらないものとする。
            Set<Agent> voteCandidates = new HashSet<>(beliefDomain);
            voteCandidates.retainAll(aliveOthers);
            Agent votedAgentByMe = brain.getPinpointEstimation_inSet(voteTargetRole, voteCandidates);
            
            label_01:
            for (Content talkContent : talkChoices) {
                double eu = 0;
                int worldCounter = 0;
                for (Map.Entry<RoleProfile, Double> entry : brain.belief.entrySet()) {
                    worldCounter++;
                    RoleProfile rp = entry.getKey();
                    
                    // 投票をカウントする
                    HashMap<Agent, Integer> voteCount = new HashMap<>();
                    
                    // 投票の有権者となる，生存者の皆さまについて
                    for (Agent agent : aliveOthers) {
                        Role ownRole = rp.getRole(agent);
                        if (ownRole == Role.ANY) {
                            // ownRole = Role.VILLAGER;
                            continue;
                        }
                        Role targetRole;
                        if (ownRole.getTeam() == Team.WEREWOLF) {
                            targetRole = Role.SEER;
                        } else {
                            targetRole = Role.WEREWOLF;
                        }
                        Agent votedAgent = brain.getVotedAgent_addingMyTalk(agent, ownRole, targetRole, talkContent.getText());
                        voteCount.put(votedAgent, voteCount.getOrDefault(votedAgent, 0) + 1);
                        // simpleLogWithoutNewLine(agent.getAgentIdx() + "->" + votedAgent.getAgentIdx() + ", ");
                    }
                    
                    // 主人公の投票先を反映（主人公の投票先（votedAgentByMe）の決定はループに入る前にやっています。）
                    voteCount.put(votedAgentByMe, voteCount.getOrDefault(votedAgentByMe, 0) + 1);
                    
                    // voteCount を数える
                    int maxVote = 0;
                    List<Agent> argmaxVote = new ArrayList<>();
                    for (Map.Entry<Agent, Integer> voteCountEntry : voteCount.entrySet()) {
                        if (maxVote < voteCountEntry.getValue()) {
                            maxVote = voteCountEntry.getValue();
                            argmaxVote.clear();
                            argmaxVote.add(voteCountEntry.getKey());
                        } else if (maxVote == voteCountEntry.getValue()) {
                            argmaxVote.add(voteCountEntry.getKey());
                        }
                    }
                    
                    double utilityForVillagerTeam = 0;
                    if (argmaxVote.size() == 1) {
                        utilityForVillagerTeam = getPayoff(1, rp.getRole(argmaxVote.get(0)));
                    } else {
                        for (Agent agent : argmaxVote) {
                            utilityForVillagerTeam += getPayoff(1, rp.getRole(agent));
                        }
                        utilityForVillagerTeam /= argmaxVote.size();
                    }
                    
                    // simpleLog(me.getAgentIdx() + "->" + votedAgentByMe.getAgentIdx() + " ==> my payoff == " + (utilityForVillagerTeam * isVillagerTeam));
                    
                    eu += entry.getValue() * utilityForVillagerTeam * isVillagerTeam;
                    
                    // 上位 worldCountLimit 個の世界を調べ終えたら，for ループを抜ける。
                    if (worldCounter >= worldCountLimit) {
                        break;
                    }
                    
                    // 制限時間が迫っている場合はループを抜ける。
                    if (System.currentTimeMillis() - start_time > 90) {
                        simpleLog("[Oops!] Abort ><");
                        expectedPayoff.put(talkContent, eu);
                        break label_01;
                    }
                }
                expectedPayoff.put(talkContent, eu);
                // simpleLog("-> " + talkContent.getText() + " == " + eu);
                computed_talk_choice_count++;
            }
            log("Number of Computed EU: " + computed_talk_choice_count);
            int entryCount = 1;
            for (Map.Entry<Content, Double> epEntry : expectedPayoff.entrySet()) {
                simpleLog(String.format("%02d", entryCount) + ") " + epEntry.getValue() + " : " + epEntry.getKey().getText());
                entryCount++;
            }
            
            Content argmax = expectedPayoff.entrySet().stream()
                    .max(Map.Entry.comparingByValue()).orElseThrow().getKey();
            
            simpleLog("Best Choice of EU " + expectedPayoff.get(argmax) + ": " + argmax.getText());
            
            if (argmax.getTopic() == Topic.VOTE) {
                if (argmax.getTarget() == declaredVoteCandidate) {
                    argmax = Content.SKIP;
                } else {
                    if (declaredVoteCandidate != null) {
                        // VOTE declaredVoteCandidate の利得が（およそ）argmax 以上であれば，何もしない。
                        Content hikaku = voteContent(me, declaredVoteCandidate);
                        if (expectedPayoff.getOrDefault(hikaku, -1.0) + 0.001 >= expectedPayoff.get(argmax)) {
                            argmax = Content.SKIP;
                        }
                    }
                }
            }
            
            manageFlagsAboutTalkContent(argmax);
            
            return argmax.getText();
        }
    }
    
    /** 発言する内容が決まった後に，その内容についてのフラグを更新する。 */
    void manageFlagsAboutTalkContent(Content argmax) {
        if (argmax.getTopic() == Topic.VOTE) {
            declaredVoteCandidate = argmax.getTarget();
        }
    }
    
    @Override
    public String whisper() {
        return null;
    }
    
    // ---------------------------------------------------------------------
    
    
    // ---------------------------------------------------------------------
    
    @Override
    public Agent vote() {
        // 生存している人のうち，いちばん voteTargetRole 度の高い人を返す。
        // （自分が人狼のときは，仲間の人狼を選ばないようにする。）
        Set<Agent> voteCandidates = new HashSet<>(beliefDomain);
        voteCandidates.retainAll(aliveOthers);
        Agent votedAgent = brain.getPinpointEstimation_inSet(voteTargetRole, voteCandidates);
        log("I'll Vote to the Most " + voteTargetRole.toString() + "-like Agent: " + votedAgent.toString());
        
        isRevote = true; // 次に（同日中に）また vote() が呼び出されたときにはtrueになっている。
        return votedAgent;
    }
    
    @Override
    public Agent attack() {
        // このメソッドは SashimiWerewolf にてオーバーライドされます。
        return null;
    }
    
    @Override
    public Agent divine() {
        // このメソッドは SashimiSeer にてオーバーライドされます。
        return null;
    }
    
    @Override
    public Agent guard() {
        return brain.getPinpointEstimation_alive(Role.SEER);
    }
    
    // ---------------------------------------------------------------------
    
    @Override
    public void finish() {
        // finish呼び出し時には，全部のエージェントの役職が公開されるようです。
    }
    
    // ---------------------------------------------------------------------
    // ---------------------------------------------------------------------
    
    // （from Sampleエージェント）
    static Content replaceSubject(Content content, Agent newSubject) {
        if (content.getTopic() == Topic.SKIP || content.getTopic() == Topic.OVER) {
            return content;
        }
        if (newSubject == Content.UNSPEC) {
            return new Content(Content.stripSubject(content.getText()));
        } else {
            return new Content(newSubject + " " + Content.stripSubject(content.getText()));
        }
    }
    
    // 再帰的に文を解析する（from Sampleエージェント）
    void parseSentence(Content content) {
        switch (content.getTopic()) {
            case COMINGOUT:
                comingoutMap.put(content.getTarget(), content.getRole());
                if (content.getRole() == Role.SEER) {
                    declaredSeers.add(content.getTarget());
                }
                return;
            case DIVINED:
                // divinationList.add(new Judge(day, content.getSubject(), content.getTarget(), content.getResult()));
                return;
            case IDENTIFIED:
                // identList.add(new Judge(day, content.getSubject(), content.getTarget(), content.getResult()));
                return;
            case OPERATOR:
                parseOperator(content);
                return;
            default:
                break;
        }
    }
    
    // 演算子文を解析する（from Sampleエージェント）
    void parseOperator(Content content) {
        switch (content.getOperator()) {
            case BECAUSE:
                parseSentence(content.getContentList().get(1));
                break;
            case DAY:
                parseSentence(content.getContentList().get(0));
                break;
            case AND:
            case OR:
            case XOR:
                for (Content c : content.getContentList()) {
                    parseSentence(c);
                }
                break;
            case REQUEST:
                /*
                if (voteRequestCounter.add(content)) {
                    return; // 投票リクエストと解析できた
                }
                 */
                break;
            case INQUIRE:
                break;
            default:
                break;
        }
    }
    
    // 発話生成を簡略化するためのwrapper（from Sampleエージェント）
    
    static Content agreeContent(Agent subject, TalkType talkType, int talkDay, int talkID) {
        return new Content(new AgreeContentBuilder(subject, talkType, talkDay, talkID));
    }
    
    static Content disagreeContent(Agent subject, TalkType talkType, int talkDay, int talkID) {
        return new Content(new DisagreeContentBuilder(subject, talkType, talkDay, talkID));
    }
    
    static Content voteContent(Agent subject, Agent target) {
        return new Content(new VoteContentBuilder(subject, target));
    }
    
    static Content votedContent(Agent subject, Agent target) {
        return new Content(new VotedContentBuilder(subject, target));
    }
    
    static Content attackContent(Agent subject, Agent target) {
        return new Content(new AttackContentBuilder(subject, target));
    }
    
    static Content attackedContent(Agent subject, Agent target) {
        return new Content(new AttackedContentBuilder(subject, target));
    }
    
    static Content guardContent(Agent subject, Agent target) {
        return new Content(new GuardCandidateContentBuilder(subject, target));
    }
    
    static Content guardedContent(Agent subject, Agent target) {
        return new Content(new GuardedAgentContentBuilder(subject, target));
    }
    
    static Content estimateContent(Agent subject, Agent target, Role role) {
        return new Content(new EstimateContentBuilder(subject, target, role));
    }
    
    static Content coContent(Agent subject, Agent target, Role role) {
        return new Content(new ComingoutContentBuilder(subject, target, role));
    }
    
    static Content requestContent(Agent subject, Agent target, Content content) {
        return new Content(new RequestContentBuilder(subject, target, content));
    }
    
    static Content inquiryContent(Agent subject, Agent target, Content content) {
        return new Content(new InquiryContentBuilder(subject, target, content));
    }
    
    static Content divinationContent(Agent subject, Agent target) {
        return new Content(new DivinationContentBuilder(subject, target));
    }
    
    static Content divinedContent(Agent subject, Agent target, Species result) {
        return new Content(new DivinedResultContentBuilder(subject, target, result));
    }
    
    static Content identContent(Agent subject, Agent target, Species result) {
        return new Content(new IdentContentBuilder(subject, target, result));
    }
    
    static Content andContent(Agent subject, Content... contents) {
        return new Content(new AndContentBuilder(subject, contents));
    }
    
    static Content orContent(Agent subject, Content... contents) {
        return new Content(new OrContentBuilder(subject, contents));
    }
    
    static Content xorContent(Agent subject, Content content1, Content content2) {
        return new Content(new XorContentBuilder(subject, content1, content2));
    }
    
    static Content notContent(Agent subject, Content content) {
        return new Content(new NotContentBuilder(subject, content));
    }
    
    static Content dayContent(Agent subject, int day, Content content) {
        return new Content(new DayContentBuilder(subject, day, content));
    }
    
    static Content becauseContent(Agent subject, Content reason, Content action) {
        return new Content(new BecauseContentBuilder(subject, reason, action));
    }
}

