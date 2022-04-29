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


public class SashimiMedium extends SashimiBasePlayer {
    
    /** （自分が）（霊媒師として）COしたかどうか */
    boolean hasComeOut;
    
    /** 人狼を見つけたかどうか */
    boolean hasFoundWerewolf;
    
    /** 自分の霊媒結果の時系列 */
    private List<Judge> myIdentList = new ArrayList<>();
    
    /** 自分の霊媒結果のマップ */
    private Map<Agent, Judge> myIdentMap = new HashMap<>();
    
    /** いままでに報告した霊媒結果 */
    private Set<Agent> myRevealedIdentSet = new HashSet<>();
    
    /** コンストラクタ */
    public SashimiMedium(LoadedModelMap lmm) {
        this.lmm = lmm;
    }
    
    @Override
    public void initialize(GameInfo gameInfo, GameSetting gameSetting) {
        super.initialize(gameInfo, gameSetting);
        isVillagerTeam = 1;
        
        hasComeOut = false;
        myIdentList = new ArrayList<>();
        myIdentMap = new HashMap<>();
        hasFoundWerewolf = false;
        myRevealedIdentSet = new HashSet<>();
    }
    
    @Override
    public void dayStart() {
        super.dayStart();
        
        // 霊媒結果を待ち行列に入れる
        Judge ident = currentGameInfo.getMediumResult();
        if (ident != null) {
            Agent identified = ident.getTarget();
            
            myIdentList.add(ident);
            myIdentMap.put(ident.getTarget(), ident);
            
            grayList.remove(identified);
            // Brainにも伝えます
            if (ident.getResult() == Species.HUMAN) {
                whiteList.add(identified);
                brain.addObviousRole_not(identified, Role.WEREWOLF);
            } else {
                hasFoundWerewolf = true;
                blackList.add(identified);
                brain.addObviousRole(identified, Role.WEREWOLF);
            }
        }
    }
    
    
    @Override
    void setWatchingTargetRoles() {
        watchingTargetRoles.add(Role.WEREWOLF);
        // watchingTargetRoles.add(Role.SEER);
        // watchingTargetRoles.add(Role.BODYGUARD);
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
        
        // 霊媒の結果
        if (day > 1 && !myIdentList.isEmpty()) {
            if (!hasComeOut) {
                for (Map.Entry<Agent, Judge> entry : myIdentMap.entrySet()) {
                    if (entry.getValue().getDay() == 2) { // 1日目の夕方に追放されたエージェントの結果について，dayは2ですかね。
                        Content content1 = andContent(me,
                                coContent(me, me, Role.MEDIUM),
                                identContent(me, entry.getValue().getTarget(), entry.getValue().getResult()));
                        talkChoices.add(content1);
                    }
                }
            } else {
                // CO済みの場合，言ってない結果を言う。
                for (Map.Entry<Agent, Judge> entry : myIdentMap.entrySet()) {
                    if (!myRevealedIdentSet.contains(entry.getKey())) {
                        Content content1 = identContent(me, entry.getValue().getTarget(), entry.getValue().getResult());
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
            if (content.getText().contains("IDENTIFIED")) {
                // 例：Agent[09] IDENTIFIED Agent[14] WEREWOLF
                myRevealedIdentSet.add(Agent.getAgent(Integer.parseInt(content.getText().split(" ")[2].substring(6, 8))));
            }
        } else {
            if (content.getText().contains("COMINGOUT")) {
                hasComeOut = true;
                // 例：Agent[09] AND (COMINGOUT Agent[09] MEDIUM) (IDENTIFIED Agent[12] HUMAN)
                // splitして，0はじまりで6番目のAgentさんについて報告。
                myRevealedIdentSet.add(Agent.getAgent(Integer.parseInt(content.getText().split(" ")[6].substring(6, 8))));
            }
        }
    }
    
}
