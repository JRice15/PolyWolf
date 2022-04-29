package jp.ac.tsukuba.s.s2020602.belief;

import jp.ac.tsukuba.s.s2020602.utils.DebugPrint;
import org.aiwolf.common.data.Agent;
import org.aiwolf.common.data.Role;

import java.util.HashMap;
import java.util.Map;
import java.util.Set;

/** 役職プロファイル。Role.ANY を許容する。 */
public class RoleProfile implements DebugPrint {
    
    /** エージェント -> 役職 の Map */
    private Map<Agent, Role> agentRoleMap;
    
    ////////////////////////////////////////////////////////////////////////////////////////////////////
    
    /** コンストラクタ */
    public RoleProfile() {
        agentRoleMap = new HashMap<>();
    }
    
    ////////////////////////////////////////////////////////////////////////////////////////////////////
    
    /** エージェントと役職の対応づけを追加する。 */
    public void put(Agent agent, Role role) {
        agentRoleMap.put(agent, role);
    }
    
    /**
     * エージェントを受け取り，その人に対応づけられた役職を返す。
     * なにも対応付けられていない場合は，Role.ANY を返す。
     */
    public Role getRole(Agent agent) {
        return agentRoleMap.getOrDefault(agent, Role.ANY);
    }
    
    public Set<Agent> getAgentSet() {
        return agentRoleMap.keySet();
    }
    
}
