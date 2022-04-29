package jp.ac.tsukuba.s.s2020602.roles;

import jp.ac.tsukuba.s.s2020602.belief.LoadedModelMap;
import org.aiwolf.client.lib.Content;
import org.aiwolf.common.data.Agent;
import org.aiwolf.common.data.Role;
import org.aiwolf.common.net.GameInfo;
import org.aiwolf.common.net.GameSetting;

public class SashimiVillager extends SashimiBasePlayer {
    
    public SashimiVillager(LoadedModelMap lmm) {
        this.lmm = lmm;
    }
    
    @Override
    public void initialize(GameInfo gameInfo, GameSetting gameSetting) {
        super.initialize(gameInfo, gameSetting);
        isVillagerTeam = 1;
    }
    
    @Override
    void setWatchingTargetRoles() {
        if (villageSize == 5) {
            watchingTargetRoles.add(Role.SEER);
            watchingTargetRoles.add(Role.WEREWOLF);
            watchingTargetRoles.add(Role.POSSESSED);
        } else {
            watchingTargetRoles.add(Role.WEREWOLF);
            // watchingTargetRoles.add(Role.SEER);
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
        // talkChoices に，発言の選択肢を格納する．
        
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
