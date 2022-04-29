package jp.ac.tsukuba.s.s2020602.utils;

import org.aiwolf.common.data.Role;

import java.io.*;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.text.SimpleDateFormat;
import java.util.*;

public class RunUsingStarter {
    
    /** "Sashimi" -> "Sashimi,java,jp.ac.tsukuba.s.s2020602.SashimiRoleAssignPlayer" のようにマッピングする Map */
    static Map<String, String> agents = new HashMap<>();
    
    /** 標準出力のままにするかどうか。false なら，output.txt に出力する。 */
    static boolean toStdOutput = true;
    
    public static void main(String[] args) throws IOException {
        main2();
    }
    
    public static void main2() throws IOException {
        
        int setNum = 1;  // 何セット行いますか。
        int gameNum = 1;  // 1セットに何回ゲームをしますか。
        int villageSize = 15;  // 何人村にしますか。
        
        boolean onlySamples = false; // テスト用に，サンプルだけで実行するとき true にする。
        
        if (gameNum * setNum > 19) {
            // ゲームの量が多いときは，標準出力ではなく，output.txt にする。
            toStdOutput = false;
        }
        
        String aiwolfLogDir = "/Users/sashimi/aiwolf_log/";
        
        String logParentDirectory = aiwolfLogDir
                + (new SimpleDateFormat("yyyy-MM-dd/HHmmss").format(new Date()))
                + "_v" + String.format("%02d", villageSize) + "_" + gameNum + "x" + setNum;
        
        // フォルダを作っておく
        Files.createDirectories(Paths.get(logParentDirectory));
        
        ResultStructure resultStructure = new ResultStructure();
        
        
        // （必ず参加するエージェント）
        Map<String, String> sashimiAgents = new HashMap<String, String>() {{
            // ,VILLAGER をつけることもできますよ。
            put("Shimi1", "Sashim1,java,jp.ac.tsukuba.s.s2020602.SashimiRoleAssignPlayer"); // me
            // put("Sample", "Sample,java,org.aiwolf.sample.player.SampleRoleAssignPlayer"); // sample
        }};
        
        if (onlySamples) {
            for (int i = 1; sashimiAgents.size() < villageSize; i++) {
                sashimiAgents.put(String.format("Smpl%02d", i), String.format("Smpl%02d,java,org.aiwolf.sample.player.SampleRoleAssignPlayer", i));
            }
        }
        
        /* 【エージェントの追加方法】
         * agentsディレクトリにjarを追加して，モジュール設定で「依存関係」のところにjarを追加する。
         * Javaの場合，クラスパスにはRoleAssignPlayer の「参照をコピー」したものを使えばよいはず。
         * ジェネレータを使って作られたエージェントの場合，TakedaRoleAssignPlayer ではなく，
         * エージェント固有のクラスがあるはずなので，それをクラスパスに指定する。
         * Python の場合，./agents/ から始めて，メインファイル（？）.py までのパスを書けばよいはず。
         */ // <- エージェントの追加方法
        
        // 参加するエージェント
        
        // 5人村にも参加してほしいエージェント
        Map<String, String> priorityAgents = new HashMap<String, String>() {{
            // put("Sample", "Sample,java,org.aiwolf.sample.player.SampleRoleAssignPlayer"); // sample
        }};
        
        // そのほかのエージェント
        Map<String, String> otherAgents = new HashMap<String, String>() {{
            // put("Sample", "Sample,java,org.aiwolf.sample.player.SampleRoleAssignPlayer");  // sample
        }};
        
        // セットごとのイテレーション
        for (int iii = 0; iii < setNum; iii++) {
            agents.clear();
            
            // 優先度順にメンバーに入れる。
            prepareAgents:
            {
                // sashimiAgents を全部入れる
                for (Map.Entry<String, String> entry : sashimiAgents.entrySet()) {
                    agents.put(entry.getKey(), entry.getValue());
                    if (agents.size() >= villageSize) {
                        break prepareAgents;
                    }
                }
                
                // priorityAgents から，入るだけ入れる
                List<Map.Entry<String, String>> agentList = new ArrayList<>(priorityAgents.entrySet());
                Collections.shuffle(agentList);
                for (Map.Entry<String, String> agentEntry : agentList) {
                    agents.put(agentEntry.getKey(), agentEntry.getValue());
                    if (agents.size() >= villageSize) {
                        break prepareAgents;
                    }
                }
                
                // otherAgents から，入るだけ入れる
                agentList = new ArrayList<>(otherAgents.entrySet());
                Collections.shuffle(agentList);
                for (Map.Entry<String, String> agentEntry : agentList) {
                    agents.put(agentEntry.getKey(), agentEntry.getValue());
                    if (agents.size() >= villageSize) {
                        break prepareAgents;
                    }
                }
                
                // Sample を，入るだけ入れる
                for (int i = 1; agents.size() < villageSize; i++) {
                    agents.put(String.format("Smpl%02d", i), String.format("Smpl%02d,java,org.aiwolf.sample.player.SampleRoleAssignPlayer", i));
                }
            }
            
            System.out.println(agents.size() + " agents: " + agents.keySet());
            
            String logSubDirectoryProperty = logParentDirectory + "/" + String.format("%03d", iii);
            
            // 標準出力をファイルにするためにフォルダを作っておく
            Files.createDirectories(Paths.get(logSubDirectoryProperty));
            
            FileOutputStream fos;
            fos = new FileOutputStream(logSubDirectoryProperty + "/output.txt");
            // 現在の標準出力先を保持する
            PrintStream sysOut = System.out;
            // 標準出力の出力先をファイルに切り変える
            PrintStream ps = new PrintStream(fos);
            if (!toStdOutput) {
                System.setOut(ps);
            }
            
            startGame(gameNum, "log=" + logSubDirectoryProperty, agents);
            
            System.out.println("-----\nここにきています。\n-----");
            
            ps.close();
            fos.close();
            // 標準出力をデフォルトに戻す
            System.setOut(sysOut);
            
            // 結果を処理
            // resultStructure.addResults(line);
            File resultFile = new File(logSubDirectoryProperty + "/result.tsv");
            LineNumberReader br = new LineNumberReader(new FileReader(resultFile));
            String line = br.readLine();
            while (line != null) {
                if (2 <= br.getLineNumber() && br.getLineNumber() <= 1 + villageSize) {
                    resultStructure.addResults(line);
                }
                // System.out.println(line);
                line = br.readLine();
            }
            br.close();
        }
        
        // resultStructure の内容をファイルに書き出します。
        File totalResultFile = new File(String.format("%s/total_result.tsv", logParentDirectory)); // <- tsvファイル
        FileWriter filewriter = new FileWriter(totalResultFile);
        filewriter.write("agent\tBODYGUARD\tMEDIUM\tPOSSESSED\tSEER\tVILLAGER\tWEREWOLF\tTotal\tWin\n");
        for (Map.Entry<String, AgentResult> entry : resultStructure.map.entrySet()) {
            // Sashim1	0/0	0/0	0/0	0/1	0/0	0/0	2/10    0.000
            // String line = entry.getKey() ;
            filewriter.write(entry.getValue().getAgentResult());
        }
        filewriter.close();
    }
    
    static void startGame(int gameNum, String logDirectoryProperty, Map<String, String> agentSet) throws IOException {
        System.out.println("-----\nスタートします。");
        System.out.println(agentSet.keySet() + "\n-----");
        
        FileWriter fileWriter = new FileWriter("./lib/AutoStarter_now.ini", false);
        fileWriter.write(""
                + "#################################################################\n"
                + "##### このファイルは編集しないでください！\n"
                + "##### （RunUsingStarter を実行すると 上書きされてしまいます！）\n"
                + "#################################################################\n");
        
        fileWriter.write("" +
                // おまじない
                "lib=./\n" +
                "port=10000\n" +
                "view=false\n" +
                "setting=./lib/SampleSetting.cfg\n" +
                // ログの場所
                logDirectoryProperty + "\n" +
                // ゲームの数
                "game=" + gameNum + "\n" +
                // エージェント数
                "agent=" + agentSet.size() + "\n");
        
        // 各エージェントの記述
        for (String agentProperty : agentSet.values()) {
            fileWriter.write(agentProperty + "\n");
        }
        fileWriter.close();
        
        MyAutoStarter autoStarter = new MyAutoStarter("./lib/AutoStarter_now.ini");
        
        try {
            autoStarter.start();
            autoStarter.result();
        } catch (InstantiationException | IllegalAccessException | ClassNotFoundException e) {
            e.printStackTrace();
        }
        
    }
    
}

class ResultStructure {
    Map<String, AgentResult> map;
    
    ResultStructure() {
        map = new HashMap<>();
    }
    
    void addResults(String line) {
        String[] agentNameArray = line.split("\t");
        String agentName = agentNameArray[0];
        if (!map.containsKey(agentName)) {
            // System.out.println("==========");
            System.out.println(map.keySet() + " に " + agentName + " が含まれていないので，putします。");
            // System.out.println("==========");
            map.put(agentName, new AgentResult(agentName));
        }
        // System.out.println("addResults：" + line);
        map.get(agentName).addAgentResult(line);
    }
}

class AgentResult {
    String name;
    TreeMap<Role, Integer> win_count;
    TreeMap<Role, Integer> game_count;
    int win_total_count;
    int game_total_count;
    
    AgentResult(String name) {
        this.name = name;
        win_count = new TreeMap<Role, Integer>() {{
            put(Role.BODYGUARD, 0);
            put(Role.MEDIUM, 0);
            put(Role.POSSESSED, 0);
            put(Role.SEER, 0);
            put(Role.VILLAGER, 0);
            put(Role.WEREWOLF, 0);
        }};
        game_count = new TreeMap<Role, Integer>() {{
            put(Role.BODYGUARD, 0);
            put(Role.MEDIUM, 0);
            put(Role.POSSESSED, 0);
            put(Role.SEER, 0);
            put(Role.VILLAGER, 0);
            put(Role.WEREWOLF, 0);
        }};
        win_total_count = 0;
        game_total_count = 0;
    }
    
    String getAgentResult() {
        StringJoiner sj = new StringJoiner("\t");
        sj.add(name);
        sj.add(win_count.get(Role.BODYGUARD) + "/" + game_count.get(Role.BODYGUARD));
        sj.add(win_count.get(Role.MEDIUM) + "/" + game_count.get(Role.MEDIUM));
        sj.add(win_count.get(Role.POSSESSED) + "/" + game_count.get(Role.POSSESSED));
        sj.add(win_count.get(Role.SEER) + "/" + game_count.get(Role.SEER));
        sj.add(win_count.get(Role.VILLAGER) + "/" + game_count.get(Role.VILLAGER));
        sj.add(win_count.get(Role.WEREWOLF) + "/" + game_count.get(Role.WEREWOLF));
        sj.add(win_total_count + "/" + game_total_count);
        double winRate = (double) win_total_count / (double) game_total_count;
        sj.add(String.format("%.3f\n", winRate));
        return sj.toString();
    }
    
    void addAgentResult(String line) {
        // 長さ：8
        String[] data = line.split("\t");
        // 名前が違うときはリターンする
        // if (data[0].equals(name)) { return; }
        
        String[] bodyguard = data[1].split("/");
        win_count.put(Role.BODYGUARD, win_count.get(Role.BODYGUARD) + Integer.parseInt(bodyguard[0]));
        game_count.put(Role.BODYGUARD, game_count.get(Role.BODYGUARD) + Integer.parseInt(bodyguard[1]));
        
        String[] medium = data[2].split("/");
        win_count.put(Role.MEDIUM, win_count.get(Role.MEDIUM) + Integer.parseInt(medium[0]));
        game_count.put(Role.MEDIUM, game_count.get(Role.MEDIUM) + Integer.parseInt(medium[1]));
        
        String[] possessed = data[3].split("/");
        win_count.put(Role.POSSESSED, win_count.get(Role.POSSESSED) + Integer.parseInt(possessed[0]));
        game_count.put(Role.POSSESSED, game_count.get(Role.POSSESSED) + Integer.parseInt(possessed[1]));
        
        String[] seer = data[4].split("/");
        win_count.put(Role.SEER, win_count.get(Role.SEER) + Integer.parseInt(seer[0]));
        game_count.put(Role.SEER, game_count.get(Role.SEER) + Integer.parseInt(seer[1]));
        
        String[] villager = data[5].split("/");
        win_count.put(Role.VILLAGER, win_count.get(Role.VILLAGER) + Integer.parseInt(villager[0]));
        game_count.put(Role.VILLAGER, game_count.get(Role.VILLAGER) + Integer.parseInt(villager[1]));
        
        String[] werewolf = data[6].split("/");
        win_count.put(Role.WEREWOLF, win_count.get(Role.WEREWOLF) + Integer.parseInt(werewolf[0]));
        game_count.put(Role.WEREWOLF, game_count.get(Role.WEREWOLF) + Integer.parseInt(werewolf[1]));
        
        win_total_count += Integer.parseInt(bodyguard[0]) + Integer.parseInt(medium[0]) + Integer.parseInt(possessed[0]) + Integer.parseInt(seer[0]) + Integer.parseInt(villager[0]) + Integer.parseInt(werewolf[0]);
        game_total_count += Integer.parseInt(bodyguard[1]) + Integer.parseInt(medium[1]) + Integer.parseInt(possessed[1]) + Integer.parseInt(seer[1]) + Integer.parseInt(villager[1]) + Integer.parseInt(werewolf[1]);
    }
    
}