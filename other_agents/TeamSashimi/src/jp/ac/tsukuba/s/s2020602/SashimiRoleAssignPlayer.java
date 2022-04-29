package jp.ac.tsukuba.s.s2020602;

import jp.ac.tsukuba.s.s2020602.belief.LoadedModelMap;
import org.aiwolf.common.data.Player;
import org.aiwolf.sample.lib.AbstractRoleAssignPlayer;

public class SashimiRoleAssignPlayer extends AbstractRoleAssignPlayer {
    
    @Override
    public String getName() {
        return "SashimiRoleAssignPlayer";
    }
    
    public SashimiRoleAssignPlayer() {
        // まず，fastText の学習済みモデルをロードさせていただきたく存じます。
        LoadedModelMap lmm = new LoadedModelMap();
        
        Player myPlayer = new SashimiPlayer(lmm);
        
        setVillagerPlayer(myPlayer);
        setSeerPlayer(myPlayer);
        setBodyguardPlayer(myPlayer);
        setMediumPlayer(myPlayer);
        setWerewolfPlayer(myPlayer);
        setPossessedPlayer(myPlayer);
    }
    
}