package jp.ac.tsukuba.s.s2020602.roles;

import jp.ac.tsukuba.s.s2020602.belief.LoadedModelMap;
import org.aiwolf.client.lib.Content;
import org.aiwolf.common.data.Agent;
import org.aiwolf.common.data.Role;
import org.aiwolf.common.net.GameInfo;
import org.aiwolf.common.net.GameSetting;


public class SashimiBodyguard extends SashimiBasePlayer {
    
    public SashimiBodyguard(LoadedModelMap lmm) {
        this.lmm = lmm;
    }
    
    @Override
    public void initialize(GameInfo gameInfo, GameSetting gameSetting) {
        super.initialize(gameInfo, gameSetting);
        isVillagerTeam = 1;
    }
    
    @Override
    void setWatchingTargetRoles() {
        watchingTargetRoles.add(Role.WEREWOLF);
        // watchingTargetRoles.add(Role.SEER);
        // watchingTargetRoles.add(Role.MEDIUM);
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
        
        // log("talkChoices: " + talkChoices);
    }
}
