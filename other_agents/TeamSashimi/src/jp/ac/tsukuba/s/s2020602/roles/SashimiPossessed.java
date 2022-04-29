package jp.ac.tsukuba.s.s2020602.roles;

import jp.ac.tsukuba.s.s2020602.belief.LoadedModelMap;
import org.aiwolf.client.lib.Content;
import org.aiwolf.common.data.Agent;
import org.aiwolf.common.data.Judge;
import org.aiwolf.common.data.Role;
import org.aiwolf.common.data.Species;
import org.aiwolf.common.net.GameInfo;
import org.aiwolf.common.net.GameSetting;

import java.util.LinkedHashMap;
import java.util.Map;

public class SashimiPossessed extends SashimiBasePlayer {
    
    /** COした役職 */
    private Role myFakeRole = Role.ANY;
    
    /** いままでに報告した占い結果の Agent と Judge の Map */
    private Map<Agent, Judge> myRevealedDivinationMap = new LinkedHashMap<>();
    
    /** そのターンに占い結果を言う必要があるときに true になるフラグ */
    private boolean needReportJudge = false;
    
    /** コンストラクタ */
    public SashimiPossessed(LoadedModelMap lmm) {
        this.lmm = lmm;
    }
    
    @Override
    public void initialize(GameInfo gameInfo, GameSetting gameSetting) {
        super.initialize(gameInfo, gameSetting);
        isVillagerTeam = -1;
        
        myFakeRole = Role.ANY;
        myRevealedDivinationMap = new LinkedHashMap<>();
        needReportJudge = false;
    }
    
    @Override
    void setWatchingTargetRoles() {
        if (villageSize == 5) {
            watchingTargetRoles.add(Role.SEER);
            watchingTargetRoles.add(Role.WEREWOLF);
            watchingTargetRoles.add(Role.VILLAGER);
        } else {
            watchingTargetRoles.add(Role.WEREWOLF);
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
            // すぐ CO するようにする
            needComingoutSeer = true;
            // log("狂人なので，占い師 CO するスイッチを入れました。");
            log("Because I'm a POSSESSED, I'll CO as a SEER.");
        }
    }
    
    @Override
    void updateTalkChoices() {
        talkChoices.clear();
        
        // 占い師を騙る文
        if (myFakeRole == Role.ANY && declaredSeers.size() < 3) {
            // 自分が未 CO で，自分以外に自称占い師が2人以下のとき，選択肢に入れる。
            for (Agent targetAgent : aliveOthers) {  // allOthers だと，生存してないエージェントを占うことがあるため，aliveOthers を使う。
                Content content1 = andContent(me, coContent(me, me, Role.SEER), dayContent(me, 1, divinedContent(me, targetAgent, Species.WEREWOLF)));
                talkChoices.add(content1);
                Content content2 = andContent(me, coContent(me, me, Role.SEER), dayContent(me, 1, divinedContent(me, targetAgent, Species.HUMAN)));
                talkChoices.add(content2);
            }
            // 必ず CO するときは，ここでリターン
            if (needComingoutSeer) {
                return;
            }
        } else if (myFakeRole == Role.SEER && myRevealedDivinationMap.size() < day) {
            // 何日目の占いとして報告するか
            int judgeDay = myRevealedDivinationMap.size() + 1;
            
            for (Agent targetAgent : aliveOthers) {  // allOthers だと，生存してないエージェントを占うことがあるため，aliveOthers を使う。
                if (myRevealedDivinationMap.containsKey(targetAgent)) {
                    continue;
                }
                Content content1 = dayContent(me, judgeDay, divinedContent(me, targetAgent, Species.WEREWOLF));
                talkChoices.add(content1);
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
        
        // ピンポイントで「この人は人狼です」と言える人の数？
        int tmpCount = 0;
        
        if (!myRevealedDivinationMap.isEmpty()) {
            for (Map.Entry<Agent, Judge> entry : myRevealedDivinationMap.entrySet()) {
                if (entry.getValue().getResult() == Species.WEREWOLF && aliveOthers.contains(entry.getKey())) {
                    tmpCount++;
                    Content content = voteContent(me, entry.getKey());
                    talkChoices.add(content);
                }
            }
        }
        
        // ピンポイントで「この人は人狼です」と言える人がいなかったとき
        if (tmpCount < 1) {
            // VOTE文
            for (Agent targetAgent : aliveOthers) {
                Content content1 = voteContent(me, targetAgent);
                talkChoices.add(content1);
                
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
        
        // co役職の管理
        // myRevealedDivinationSetの管理
        
        try {
            
            if (myFakeRole == Role.SEER) { // 占い師をCO済みのとき
                if (content.getText().contains("DIVINED")) {
                    // 例：Agent[09] DAY 2 (DIVINED Agent[06] HUMAN)
                    
                    String[] contentData = content.getText().split(" ");
                    int judgeDay = Integer.parseInt(contentData[2]);
                    Agent targetAgent = Agent.getAgent(Integer.parseInt(contentData[4].substring(6, 8)));
                    Species result = contentData[5].startsWith("HUMAN") ? Species.HUMAN : Species.WEREWOLF;
                    
                    myRevealedDivinationMap.put(targetAgent, new Judge(judgeDay, me, targetAgent, result));
                    
                    needReportJudge = false;
                }
            } else { // 未 CO のとき
                
                if (content.getText().contains("COMINGOUT")) {
                    // 例：Agent[09] AND (COMINGOUT Agent[09] SEER) (DAY 1 (DIVINED Agent[14] WEREWOLF))
                    
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
}
