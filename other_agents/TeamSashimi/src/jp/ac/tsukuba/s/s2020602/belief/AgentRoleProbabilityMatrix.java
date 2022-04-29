package jp.ac.tsukuba.s.s2020602.belief;

import jp.ac.tsukuba.s.s2020602.utils.DebugPrint;
import org.aiwolf.common.data.Agent;
import org.aiwolf.common.data.Role;

import java.util.*;

/** 「エージェントがその役職である確率」を表すためのクラス。自分以外のプレイヤーについて考える。 */
public class AgentRoleProbabilityMatrix implements DebugPrint {
    
    /** 自分 */
    Agent me;
    
    /** 「各エージェントが各役職である確率」を表す本体 */
    private Map<Agent, Map<Role, Double>> agentRoleProbabilityMap;
    
    /** targetRolesを記憶しておくためのリスト */
    ArrayList<Role> targetRoleList;
    
    /** ホワイトリスト（役職が人狼ではないと判明した人たち） */
    Set<Agent> whiteList;
    
    /** ブラックリスト（役職が人狼であると判明した人たち） */
    Set<Agent> blackList;
    
    /** グレーリスト（役職が人狼であるとも人狼でないとも判明していない人たち） */
    Set<Agent> grayList;
    
    /** コンストラクタ */
    public AgentRoleProbabilityMatrix(Collection<Agent> targetAgents, Collection<Role> targetRoles) {
        agentRoleProbabilityMap = new HashMap<>();
        double initProb = 1.0 / ((double) targetRoles.size());
        this.targetRoleList = new ArrayList<>(targetRoles);
        
        for (Agent targetAgent : targetAgents) {
            Map<Role, Double> roleMap = new HashMap<>();
            for (Role targetRole : targetRoles) {
                roleMap.put(targetRole, initProb);
            }
            agentRoleProbabilityMap.put(targetAgent, roleMap);
        }
        
        // 各種カラーリストの初期化
        whiteList = new HashSet<>();
        blackList = new HashSet<>();
        grayList = new HashSet<>(targetAgents);
    }
    
    /** 与えられたエージェントと役職と double 値 prob について，そのエージェントがその役職である確率を prob に設定します。 */
    public void setAgentRoleProbability(Agent targetAgent, Role targetRole, double prob) {
        if (targetRoleList.contains(targetRole) && targetAgent != me) {
            // targetAgent さんの targetRole 度を更新する
            agentRoleProbabilityMap.get(targetAgent).put(targetRole, prob);
        } else {
            // targetAgent さんの targetRole 度を変更しようと思いましたが，この役職は推定の対象外でした。
            log("Failed to update P(" + targetAgent.getAgentIdx() + ", " + toKanji(targetRole) + "). Out of Ganchu of estimation.");
        }
    }
    
    /** 与えられたエージェントと役職について，そのエージェントがその役職である確率を返します。 */
    public double getAgentRoleProbability(Agent targetAgent, Role targetRole) {
        return agentRoleProbabilityMap.get(targetAgent).get(targetRole);
    }
    
    /** 各エージェントについて，確率の和が 1 になるようにする。 */
    public void setProbSumToOneForEachAgent() {
        // まず，カラーリストを反映します。
        
        // blackList に含まれるエージェントは，全員人狼です。
        for (Agent blackAgent : blackList) {
            // 人狼度を1にして，その他の役職度を0にする。
            setAgentRoleProbability(blackAgent, Role.WEREWOLF, 1.0);
            for (Role targetRole : targetRoleList) {
                if (targetRole != Role.WEREWOLF) {
                    setAgentRoleProbability(blackAgent, targetRole, 0);
                }
            }
        }
        
        // whiteList に含まれるエージェントは，全員とも人狼ではありません。
        for (Agent whiteAgent : whiteList) {
            // 人狼度を0にする。
            setAgentRoleProbability(whiteAgent, Role.WEREWOLF, 0);
        }
        
        for (Agent targetAgent : agentRoleProbabilityMap.keySet()) {
            double sum = 0.0;
            for (double prob : agentRoleProbabilityMap.get(targetAgent).values()) {
                sum += prob;
            }
            double scale = 1.0 / sum;
            for (Map.Entry<Role, Double> entry : agentRoleProbabilityMap.get(targetAgent).entrySet()) {
                double exVal = entry.getValue();
                agentRoleProbabilityMap.get(targetAgent).put(entry.getKey(), exVal * scale);
            }
        }
    }
    
}
