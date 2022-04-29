package jp.ac.tsukuba.s.s2020602.roles;

import jp.ac.tsukuba.s.s2020602.belief.LoadedModelMap;
import org.aiwolf.client.lib.Content;
import org.aiwolf.common.data.*;
import org.aiwolf.common.net.GameInfo;
import org.aiwolf.common.net.GameSetting;

import java.util.*;

//import static jp.ac.tsukuba.s.s2020602.utils.LogPrint.log;

public class SashimiWerewolf extends SashimiBasePlayer {
    
    /** COした役職 */
    private Role myFakeRole = Role.ANY;
    
    /** いままでに報告した占い結果の Agent と Judge の Map */
    private Map<Agent, Judge> myRevealedDivinationMap = new LinkedHashMap<>();
    
    /** そのターンに占い結果を言う必要があるときに true になるフラグ */
    private boolean needReportJudge = false;
    
    /** ささやきが必要かどうか */
    boolean needWhisper;
    
    /** ささやきリスト読み込みのヘッド */
    private int whisperListHead;
    
    /** 人狼たちの偽のCOの予定 */
    private Map<Agent, Role> fakeComingoutPlanMap = new HashMap<>();
    
    
    /** コンストラクタ */
    public SashimiWerewolf(LoadedModelMap lmm) {
        this.lmm = lmm;
    }
    
    @Override
    public void initialize(GameInfo gameInfo, GameSetting gameSetting) {
        super.initialize(gameInfo, gameSetting);
        
        needWhisper = false;
        
        isVillagerTeam = -1;
        
        myFakeRole = Role.ANY;
        myRevealedDivinationMap = new LinkedHashMap<>();
        needReportJudge = false;
        
        needComingoutSeer = false;
        
        whisperListHead = 0;
        fakeComingoutPlanMap.clear();
    }
    
    
    @Override
    void setWatchingTargetRoles() {
        if (villageSize == 5) {
            watchingTargetRoles.add(Role.SEER);
            watchingTargetRoles.add(Role.VILLAGER);
            watchingTargetRoles.add(Role.POSSESSED);
        } else {
            watchingTargetRoles.add(Role.POSSESSED);
            watchingTargetRoles.add(Role.SEER);
            watchingTargetRoles.add(Role.BODYGUARD);
            // watchingTargetRoles.add(Role.MEDIUM);
        }
    }
    
    @Override
    void setVoteTargetRole() {
        voteTargetRole = Role.SEER;
    }
    
    @Override
    public void dayStart() {
        super.dayStart();
        
        if (myFakeRole == Role.SEER) {
            // 占い師CO済みなら，結果報告すべし
            needReportJudge = true;
        } else {
            // CO してないとき
            // 5人村では占い師COする
            if (villageSize == 5) {
                needComingoutSeer = true;
                log("Because I'm a WEREWOLF in v05, I'll CO as a SEER.");
            }
        }
    }
    
    @Override
    void updateTalkChoices() {
        talkChoices.clear();
        
        // 占い師を騙る文
        // （未COで，かつ）needComingoutSeer が true のときだけ，騙ることを選択肢に入れる
        if (myFakeRole == Role.ANY && needComingoutSeer) {
            for (Agent targetAgent : aliveOthers) {  // allOthers だと，生存してないエージェントを占うことがあるため，aliveOthers を使う。
                if (currentGameInfo.getRoleMap().getOrDefault(targetAgent, Role.ANY) != Role.WEREWOLF) {
                    // 自分以外の人狼に対しては黒出しを控える
                    Content content1 = andContent(me, coContent(me, me, Role.SEER), dayContent(me, 1, divinedContent(me, targetAgent, Species.WEREWOLF)));
                    talkChoices.add(content1);
                }
                // 白出しは全員を対象としてみる
                Content content2 = andContent(me, coContent(me, me, Role.SEER), dayContent(me, 1, divinedContent(me, targetAgent, Species.HUMAN)));
                talkChoices.add(content2);
            }
            // 必ず CO するために，ここでリターン
            return;
        } else if (myFakeRole == Role.SEER && myRevealedDivinationMap.size() < day) {
            // 占い結果報告をする可能性がある
            
            // 何日目の占いとして報告するか
            int judgeDay = myRevealedDivinationMap.size() + 1;
            
            for (Agent targetAgent : aliveOthers) {  // allOthers だと，生存してないエージェントを占うことがあるため，aliveOthers を使う。
                if (myRevealedDivinationMap.containsKey(targetAgent)) {
                    // すでに結果報告済みの人は対象外です
                    continue;
                }
                if (currentGameInfo.getRoleMap().getOrDefault(targetAgent, Role.ANY) != Role.WEREWOLF) {
                    // 自分以外の人狼に対しては黒出しを控える
                    Content content1 = dayContent(me, judgeDay, divinedContent(me, targetAgent, Species.WEREWOLF));
                    talkChoices.add(content1);
                }
                // 白出しは全員を対象としてみる
                Content content2 = dayContent(me, judgeDay, divinedContent(me, targetAgent, Species.HUMAN));
                talkChoices.add(content2);
            }
            
            // 必ず結果報告するときは，ここでリターン
            if (needReportJudge) {
                return;
            }
        }
        
        // まずは，SKIPの発言
        talkChoices.add(Content.SKIP);
        
        // ピンポイントで人狼だと指せる人の数？
        int tmpCount = 0;
        
        if (!myRevealedDivinationMap.isEmpty()) {
            for (Map.Entry<Agent, Judge> entry : myRevealedDivinationMap.entrySet()) {
                if (entry.getValue().getResult() == Species.WEREWOLF && aliveOthers.contains(entry.getKey())) {
                    // 私から黒出し済みで，かつ生存してる人が対象
                    tmpCount++;
                    Content content = voteContent(me, entry.getKey());
                    talkChoices.add(content);
                }
            }
        }
        
        // ピンポイントで人狼だと指せる人がいなかったとき
        if (tmpCount < 1) {
            // VOTE文
            for (Agent targetAgent : aliveOthers) {
                Content content = voteContent(me, targetAgent);
                talkChoices.add(content);
                
                // 占い結果で「人狼ではない」と報告した人については，「人狼だと思う」と言わないことにする。
                if (!(myRevealedDivinationMap.containsKey(targetAgent) && (myRevealedDivinationMap.get(targetAgent).getResult()) == Species.HUMAN)) {
                    Content content2 = estimateContent(me, targetAgent, Role.WEREWOLF);
                    talkChoices.add(content2);
                }
            }
            
        }
        
        // log("talkChoices: " + talkChoices);
    }
    
    @Override
    void manageFlagsAboutTalkContent(Content content) {
        super.manageFlagsAboutTalkContent(content);
        
        try {
            
            if (myFakeRole == Role.SEER) { // 占い師をCO済みのとき
                // 占い結果報告かもしれない
                if (content.getText().contains("DIVINED")) {
                    // Agent[09] DAY 2 (DIVINED Agent[06] HUMAN)
                    
                    String[] contentData = content.getText().split(" ");
                    int judgeDay = Integer.parseInt(contentData[2]);
                    Agent targetAgent = Agent.getAgent(Integer.parseInt(contentData[4].substring(6, 8)));
                    Species result = contentData[5].startsWith("HUMAN") ? Species.HUMAN : Species.WEREWOLF;
                    
                    myRevealedDivinationMap.put(targetAgent, new Judge(judgeDay, me, targetAgent, result));
                    
                    needReportJudge = false;
                }
            } else { // 未 CO のとき
                // COかもしれない
                if (content.getText().contains("COMINGOUT")) {
                    // Agent[09] AND (COMINGOUT Agent[09] SEER) (DAY 1 (DIVINED Agent[14] WEREWOLF))
                    
                    String[] contentData = content.getText().split(" ");
                    if (contentData[4].startsWith("SEER")) {
                        myFakeRole = Role.SEER;
                        needComingoutSeer = false;
                        
                        int judgeDay = Integer.parseInt(contentData[6]);
                        Agent targetAgent = Agent.getAgent(Integer.parseInt(contentData[8].substring(6, 8)));
                        Species result = contentData[9].startsWith("HUMAN") ? Species.HUMAN : Species.WEREWOLF;
                        
                        myRevealedDivinationMap.put(targetAgent, new Judge(judgeDay, me, targetAgent, result));
                    }
                }
                
            }
            
        } catch (Exception e) {
            // Integer.parseInt() の NumberFormatException に対応
            // 一応プリントしておく
            e.printStackTrace();
        }
    }
    
    
    @Override
    public String whisper() {
        // 必要に応じて占い師COを予告する。
        
        if (needWhisper) {
            needWhisper = false;
            log("needWhisper <- false (because whispered)");
            if (needComingoutSeer) {
                return coContent(me, me, Role.SEER).getText();
            } else {
                return coContent(me, me, Role.VILLAGER).getText();
            }
        } else {
            return null;
        }
    }
    
    @Override
    public void update(GameInfo gameInfo) {
        super.update(gameInfo);
        
        if (villageSize == 5) {
            // 5人村では，占い師COすることにして，あとは何もしない
            needComingoutSeer = true;
            return;
        }
        
        // ささやきを聞く
        // GameInfo.whisperListからフェイクCO宣言を抽出
        for (int i = whisperListHead; i < currentGameInfo.getWhisperList().size(); i++) {
            Talk whisper = currentGameInfo.getWhisperList().get(i);
            log("[Read " + whisper.getAgent() + "'s Whisper] " + whisper.getText());
            Agent whisperer = whisper.getAgent();
            Content content = new Content(whisper.getText());
            
            // subjectがUNSPECの場合は発話者に入れ替える
            if (content.getSubject() == Content.UNSPEC) {
                content = replaceSubject(content, whisperer);
            }
            
            parseWhisper(content);
        }
        whisperListHead = currentGameInfo.getWhisperList().size();
        
        
        // 人狼の間から占い師が出る予定じゃないとき，私が出ます。
        // ただし，すでに declaredSeers が3人以上いる場合は，やめておきます。
        if (!fakeComingoutPlanMap.containsValue(Role.SEER) && declaredSeers.size() < 3) {
            needComingoutSeer = true;
            needWhisper = true;
            simpleLog("needWhisper <- true (No seers from wolves. I'll CO.)");
        }
        
        // 占い師をCOする人狼の人数を確認
        int numOfWerewolves_ComingoutSeer = 0;
        for (Map.Entry<Agent, Role> entry : fakeComingoutPlanMap.entrySet()) {
            if (entry.getValue() == Role.SEER) {
                numOfWerewolves_ComingoutSeer++;
            }
        }
        if (numOfWerewolves_ComingoutSeer > 1 && needComingoutSeer) {
            // 人狼から占い師が2人出ようとしてるとき。
            needComingoutSeer = false;
            needWhisper = true;
            simpleLog("needWhisper <- true (Too many seers. I'll stop COing.)");
        }
        
    }
    
    @Override
    public Agent attack() {
        // 自分以外の生存者のうち，人狼でなく，最も占い師っぽい人を襲撃する。
        Set<Agent> attackCandidates = new HashSet<>(beliefDomain);
        for (Agent candidate : attackCandidates) {
            if (!allOthers.contains(candidate)) {
                attackCandidates.remove(candidate);
            }
        }
        return brain.getPinpointEstimation_inSet(voteTargetRole, attackCandidates);
    }
    
    // from Sampleエージェント
    private void parseWhisper(Content content) {
        /*
        if (estimateReasonMap.put(content)) {
            return; // 推測文と解析
        }
        if (attackVoteReasonMap.put(content)) {
            return; // 襲撃投票宣言と解析
        }
         */
        switch (content.getTopic()) {
            case COMINGOUT: // Declaration of FCO
                fakeComingoutPlanMap.put(content.getSubject(), content.getRole());
                simpleLog("fakeComingoutPlanMap added: " + fakeComingoutPlanMap);
                return;
            default:
                break;
        }
    }
}
