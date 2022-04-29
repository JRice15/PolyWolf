package jp.ac.tsukuba.s.s2020602;

import jp.ac.tsukuba.s.s2020602.belief.LoadedModelMap;
import jp.ac.tsukuba.s.s2020602.roles.*;
import jp.ac.tsukuba.s.s2020602.utils.DebugPrint;
import jp.ac.tsukuba.s.s2020602.utils.Stopwatch;
import org.aiwolf.common.data.Agent;
import org.aiwolf.common.data.Player;
import org.aiwolf.common.data.Role;
import org.aiwolf.common.data.Status;
import org.aiwolf.common.net.GameInfo;
import org.aiwolf.common.net.GameSetting;

import java.util.HashMap;
import java.util.Map;

public class SashimiPlayer implements Player, DebugPrint {
    
    /** プレイヤー本体 */
    private SashimiBasePlayer myPlayer = null;
    
    /** 実行時間を計測するためのストップウォッチ */
    private final Stopwatch stopwatch = new Stopwatch();
    
    /** 各学習済みモデルをロードした JFsstText のインスタンスの集まり */
    LoadedModelMap lmm;
    
    /** 何ゲーム目か */
    int gameNumber = 0;
    
    /** 役職ごとのクラスのインスタンスを持っておくための Map */
    Map<Role, SashimiBasePlayer> rolePlayerMap = null;
    
    
    /** コンストラクタ */
    public SashimiPlayer(LoadedModelMap lmm) {
        this.lmm = lmm;
        rolePlayerMap = new HashMap<>() {{
            put(Role.VILLAGER, new SashimiVillager(lmm));
            put(Role.SEER, new SashimiSeer(lmm));
            put(Role.WEREWOLF, new SashimiWerewolf(lmm));
            put(Role.POSSESSED, new SashimiPossessed(lmm));
            put(Role.MEDIUM, new SashimiMedium(lmm));
            put(Role.BODYGUARD, new SashimiBodyguard(lmm));
        }};
    }
    
    @Override
    public void initialize(GameInfo gameInfo, GameSetting gameSetting) {
        stopwatch.start();
        
        // 何ゲーム目かを更新する
        gameNumber++;
        log("\n==============================" +
                "\nThis is the " + String.format("%03d", gameNumber) + "-th game." +
                "\nI'm a " + gameInfo.getRole() + ".");
        
        // 自分の役職によって，どのクラスのPlayerにするかを決める。
        myPlayer = rolePlayerMap.getOrDefault(gameInfo.getRole(), rolePlayerMap.get(Role.VILLAGER));
        
        // initialize メソッドを実行
        myPlayer.initialize(gameInfo, gameSetting);
        stopwatch.stop();
    }
    
    @Override
    public String getName() {
        stopwatch.start();
        String name = myPlayer.getName();
        stopwatch.stop();
        return name;
    }
    
    @Override
    public void update(GameInfo gameInfo) {
        stopwatch.start();
        if (gameInfo.getStatusMap().get(gameInfo.getAgent()) != Status.DEAD) {
            myPlayer.update(gameInfo);
        }
        stopwatch.stop();
    }
    
    @Override
    public void dayStart() {
        stopwatch.start();
        myPlayer.dayStart();
        stopwatch.stop();
    }
    
    @Override
    public String talk() {
        stopwatch.start();
        String talkContentString = myPlayer.talk();
        stopwatch.stop();
        return talkContentString;
    }
    
    @Override
    public String whisper() {
        stopwatch.start();
        String whisperContentString = myPlayer.whisper();
        stopwatch.stop();
        return whisperContentString;
    }
    
    @Override
    public Agent vote() {
        stopwatch.start();
        Agent agentToVote = myPlayer.vote();
        stopwatch.stop();
        return agentToVote;
    }
    
    @Override
    public Agent attack() {
        stopwatch.start();
        Agent agentToAttack = myPlayer.attack();
        stopwatch.stop();
        return agentToAttack;
    }
    
    @Override
    public Agent divine() {
        stopwatch.start();
        Agent agentToDivine = myPlayer.divine();
        stopwatch.stop();
        return agentToDivine;
    }
    
    @Override
    public Agent guard() {
        stopwatch.start();
        Agent agentToGuard = myPlayer.guard();
        stopwatch.stop();
        return agentToGuard;
    }
    
    @Override
    public void finish() {
        stopwatch.start();
        myPlayer.finish();
        stopwatch.stop();
    }
}
