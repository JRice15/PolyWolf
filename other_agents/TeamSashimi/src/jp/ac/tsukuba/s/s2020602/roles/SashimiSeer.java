package jp.ac.tsukuba.s.s2020602.roles;

import jp.ac.tsukuba.s.s2020602.belief.LoadedModelMap;
import org.aiwolf.client.lib.Content;
import org.aiwolf.common.data.Agent;
import org.aiwolf.common.data.Judge;
import org.aiwolf.common.data.Role;
import org.aiwolf.common.data.Species;
import org.aiwolf.common.net.GameInfo;
import org.aiwolf.common.net.GameSetting;

import java.util.*;


public class SashimiSeer extends SashimiBasePlayer {
    
    /** COしたかどうか */
    boolean hasComeOut;
    
    /** 自分の占い結果の時系列 */
    private List<Judge> myDivinationList = new ArrayList<>();
    
    /** 自分の占い済みエージェントと判定のマップ */
    private Map<Agent, Judge> myDivinationMap = new HashMap<>();
    
    /** いままでに報告した占い結果 */
    private Set<Agent> myRevealedDivinationSet = new HashSet<>();
    
    /** SashimiSeer のコンストラクタ。 */
    public SashimiSeer(LoadedModelMap lmm) {
        this.lmm = lmm;
    }
    
    @Override
    public void initialize(GameInfo gameInfo, GameSetting gameSetting) {
        super.initialize(gameInfo, gameSetting);
        isVillagerTeam = 1;
        
        hasComeOut = false;
        myDivinationList = new ArrayList<>();
        myDivinationMap = new HashMap<>();
        myRevealedDivinationSet = new HashSet<>();
    }
    
    @Override
    public void dayStart() {
        super.dayStart();
        
        // 占い結果の取得
        Judge divination = currentGameInfo.getDivineResult();
        if (divination != null) {
            Agent divined = divination.getTarget();
            myDivinationList.add(divination);
            
            grayList.remove(divined);
            if (divination.getResult() == Species.HUMAN) {
                whiteList.add(divined);
                // Brainにも伝えます
                brain.addObviousRole_not(divined, Role.WEREWOLF);
            } else {
                blackList.add(divined);
                // Brainにも伝えます
                brain.addObviousRole(divined, Role.WEREWOLF);
                
                // 人狼が判明したら，CO する
                needComingoutSeer = true;
                log("人狼が判明したので，占い師 CO するスイッチを入れました。");
                
                // 5人村であれば，人狼以外の人たちをホワイトリストに追加します。
                if (villageSize == 5) {
                    for (Agent agt : allOthers) {
                        if (agt != divined) {
                            whiteList.add(agt);
                            brain.addObviousRole_not(agt, Role.WEREWOLF);
                        }
                    }
                }
            }
            myDivinationMap.put(divined, divination);
        }
    }
    
    
    @Override
    void setWatchingTargetRoles() {
        if (villageSize == 5) {
            watchingTargetRoles.add(Role.VILLAGER);
            watchingTargetRoles.add(Role.WEREWOLF);
            watchingTargetRoles.add(Role.POSSESSED);
        } else {
            watchingTargetRoles.add(Role.WEREWOLF);
            // watchingTargetRoles.add(Role.POSSESSED);
            // watchingTargetRoles.add(Role.BODYGUARD);
            // watchingTargetRoles.add(Role.MEDIUM);
        }
    }
    
    @Override
    void setVoteTargetRole() {
        voteTargetRole = Role.WEREWOLF;
    }
    
    @Override
    void updateTalkChoices() {
        talkChoices.clear();
        
        // まずは，SKIPの発言
        talkChoices.add(Content.SKIP);
        
        // VOTE文
        for (Agent targetAgent : aliveOthers) {
            Content content = voteContent(me, targetAgent);
            talkChoices.add(content);
        }
        
        // ESTIMATE 文
        for (Agent targetAgent : aliveOthers) {
            Content content1 = estimateContent(me, targetAgent, Role.WEREWOLF);
            talkChoices.add(content1);
        }
        
        // 占いの結果
        if (myRevealedDivinationSet.size() < day) {
            if (hasComeOut) {
                for (Map.Entry<Agent, Judge> entry : myDivinationMap.entrySet()) {
                    if (!myRevealedDivinationSet.contains(entry.getKey())) {
                        Content content1 = dayContent(me, entry.getValue().getDay(), divinedContent(me, entry.getValue().getTarget(), entry.getValue().getResult()));
                        talkChoices.add(content1);
                    }
                }
            } else {
                for (Map.Entry<Agent, Judge> entry : myDivinationMap.entrySet()) {
                    if (entry.getValue().getDay() == 1) { // 0日目の夜に占ったもののJudgeにおいて，dayは1みたいです。
                        Content content1 = andContent(me, coContent(me, me, Role.SEER), dayContent(me, entry.getValue().getDay(), divinedContent(me, entry.getValue().getTarget(), entry.getValue().getResult())));
                        talkChoices.add(content1);
                    }
                }
            }
        }
        
        // log("talkChoices: " + talkChoices);
    }
    
    @Override
    void manageFlagsAboutTalkContent(Content content) {
        super.manageFlagsAboutTalkContent(content);
        
        if (hasComeOut) {
            if (content.getText().contains("DIVINED")) {
                // Agent[09] DAY 2 (DIVINED Agent[06] HUMAN)
                myRevealedDivinationSet.add(Agent.getAgent(Integer.parseInt(content.getText().split(" ")[4].substring(6, 8))));
            }
        }
        if (content.getText().contains("COMINGOUT")) {
            hasComeOut = true;
            needComingoutSeer = false;
            
            // Agent[09] AND (COMINGOUT Agent[09] SEER) (DAY 1 (DIVINED Agent[14] WEREWOLF))
            // splitして，0はじまりで8番目のAgentさんについて報告。
            myRevealedDivinationSet.add(Agent.getAgent(Integer.parseInt(content.getText().split(" ")[8].substring(6, 8))));
        }
    }
    
    @Override
    public Agent divine() {
        if (day == 0) {
            // 最初は，何もヒントがないので，ランダムで決める
            return randomSelect(aliveOthers);
        } else {
            // 2回目以降は，divinationCandidate（自分以外の生存者のうち，すでに占った人を除いた人たち）の中から，いちばん voteTargetRole（＝人狼）っぽい人を選ぶ。
            Set<Agent> divinationCandidate = new HashSet<>(aliveOthers);
            for (Agent agent : myDivinationMap.keySet()) {
                divinationCandidate.remove(agent);
            }
            if (divinationCandidate.isEmpty()) {
                // divinationCandidate が空になってしまったら，しかたないので，自分以外の生存者全員の中からランダムで選ぶ。
                return randomSelect(aliveOthers);
            }
            return brain.getPinpointEstimation_inSet(voteTargetRole, divinationCandidate);
        }
    }
}
