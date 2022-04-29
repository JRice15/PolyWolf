package jp.ac.tsukuba.s.s2020602.belief;

import org.aiwolf.common.data.Agent;
import org.aiwolf.common.data.Role;

import java.util.regex.Pattern;

/** イベント（各プレイヤーの発言や投票の内容，人狼による襲撃の結果など）を保持しておくリスト（実態としては StringBuilder……？） */
public class EventList {
    
    /** 目線となっているエージェントのエージェント番号（範囲：1 〜 villageSize） */
    private final int myAgentOriginalNum;
    
    /** Agent[myAgentOriginalNum] という文字列（を格納する） */
    private final String AgentOriginalString;
    
    /** 読み替えのための定数 */
    private final String Agent01 = "Agent[01]", Agentxx = "Agent[xx]";
    
    /** イベントの列たる文字列 */
    private final StringBuilder stringBuilder;
    
    ////////////////////////////////////////////////////////////////////////////////////////////////////
    
    /** コンストラクタ（引数は，目線となるエージェント。このエージェントを Agent[01] と読み替えてリストに格納します。） */
    public EventList(Agent myAgent) {
        // 空の文字列を用意する
        stringBuilder = new StringBuilder();
        // 目線エージェントの実際のエージェント番号を取得
        myAgentOriginalNum = myAgent.getAgentIdx();
        AgentOriginalString = String.format("Agent[%02d]", myAgentOriginalNum);
    }
    
    ////////////////////////////////////////////////////////////////////////////////////////////////////
    
    @Override
    public String toString() {
        return stringBuilder.toString();
    }
    
    ////////////////////////////////////////////////////////////////////////////////////////////////////
    
    /**
     * エージェント番号を読み替えたうえで，エージェントの文字列表現 Agent[00] を返す。
     * agent.toString() の代わりに，agentString(agent) を使うことになる。
     */
    String agentString(Agent agent) {
        String ret = agent.toString();
        if (myAgentOriginalNum != 1) {
            if (agent.getAgentIdx() == 1) {
                ret = AgentOriginalString;
            } else if (agent.getAgentIdx() == myAgentOriginalNum) {
                ret = Agent01;
            }
        }
        return ret;
    }
    
    /** 読み替え済みのエージェント番号を，もとに戻す。 */
    int decodeAgentNumber(int yomikaedNumber) {
        if (yomikaedNumber == myAgentOriginalNum) {
            return 1;
        } else {
            return yomikaedNumber;
        }
    }
    
    
    /** テキスト中の Agent[00] を適宜読み替えて返す。 */
    String textYomikae(String text) {
        String newText = "";
        if (myAgentOriginalNum != 1) {
            // 以下，AgentOriginalString を Agent[yy] と書くことにする。
            // 次の順に書き換える。
            // Agent[01] -> Agent[xx]
            // Agent[yy] -> Agent[01]
            // Agent[xx] -> Agent[yy]
            // 結果として，Agent[01] と Agent[yy] が入れ替わる。
            newText = text
                    .replaceAll(Pattern.quote(Agent01), Agentxx)
                    .replaceAll(Pattern.quote(AgentOriginalString), Agent01)
                    .replaceAll(Pattern.quote(Agentxx), AgentOriginalString);
        }
        return newText;
    }
    
    /** 現時点のイベント列を返す。 */
    public String getEventList() {
        return stringBuilder.toString();
    }
    
    ////////////////////////////////////////////////////////////////////////////////////////////////////
    
    /**
     * （ゲームの最初に）与えられたエージェントとその役職を記す。ゲームの最初に，自分の役職を記すときに使用する。
     * （自分が人狼なら他の人狼も一緒に記す。）
     * 自分が占い師ならば，判明した占い結果についても，これ（または addObviousRole_not のほう）を使って記す。
     */
    public void addObviousRole(Agent agent, Role role) {
        addString(agentString(agent), " is_a ", role.toString(), ".");
    }
    
    public void addObviousRole_not(Agent agent, Role role) {
        addString(agentString(agent), " is_not_a ", role.toString(), ".");
    }
    
    /** talkerさんが「talkContent」としゃべったと仮定したときのEventListを返します。 */
    public String getEventList_withTempTalk(Agent talker, String talkContent) {
        StringBuilder sb = new StringBuilder(stringBuilder);
        sb.append(" ");
        sb.append(agentString(talker));
        sb.append(" says \"");
        sb.append(textYomikae(talkContent));
        sb.append("\".");
        return sb.toString();
    }
    
    // 発話された内容（自分のものも含む。）
    // 発話のたびに呼ばれる。
    public void addTalk(Agent talker, String text) {
        addString(agentString(talker), " says \"", textYomikae(text), "\".");
    }
    
    // 投票のときに呼び出される。
    public void addVote(Agent votingAgent, Agent votedAgent) {
        addString(agentString(votingAgent), " voted_to ", agentString(votedAgent), ".");
    }
    
    // 再投票になったことを知らせる記載。
    public void addRevote() {
        addString("Revote.");
    }
    
    // 投票が終わったら呼び出される
    public void addExecution(Agent executedAgent) {
        addString(agentString(executedAgent), " is_executed.");
    }
    
    // 毎朝（1日目を除く），襲撃された人が判明したら呼び出される。
    public void addAttack(Agent attackedAgent) {
        addString(agentString(attackedAgent), " is_attacked.");
    }
    
    /** 「襲撃が失敗した」（自分が人狼のときのみ） */
    public void addAttackFailure() {
    }
    
    /** 日付が変わったら「Day 2.」などのように書く。 */
    public void addNewDay(int day) {
        addString("Day ", String.valueOf(day), ".");
    }
    
    /** 与えられた文字列を順番に stringBuilder に追加する。最初に（前の文との区切りとして）スペースを1個入れる。 */
    private void addString(String... string) {
        // 前の文との区切り
        stringBuilder.append(" ");
        // 与えられた文字列を順番に stringBuilder に追加
        for (int i = 0; i < string.length; i++) {
            stringBuilder.append(string[i]);
        }
    }
    
}
