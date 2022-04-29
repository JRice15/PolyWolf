package jp.ac.tsukuba.s.s2020602.belief;

import com.github.jfasttext.JFastText;
import jp.ac.tsukuba.s.s2020602.utils.DebugPrint;
import jp.ac.tsukuba.s.s2020602.utils.Stopwatch;
import org.aiwolf.common.data.Role;

import java.io.IOException;
import java.util.*;

/** fastText の学習済みのモデルファイルを読み込み，Map として持っておくためのクラスです。 */
public class LoadedModelMap implements DebugPrint {
    
    /** JFastText のロード済みモデルを持っておくためのMap */
    private Map<String, JFastText> modelMap;
    
    /** パターンごとに学習したモデルを使うとき true にする。
     * なお，現在は，5人村で自称占い師が2人のとき（s02）のパターンのみ，モデルが存在します。 */
    boolean useModel_s02 = true;
    
    /** コンストラクタ */
    public LoadedModelMap(int villageSize) {
        this();
    }
    
    /** コンストラクタ */
    public LoadedModelMap() {
        // ストップウォッチ スタート
        Stopwatch sw_init = new Stopwatch();
        sw_init.start();
        
        // Map を初期化
        modelMap = new HashMap<>();
        
        // プレイヤーの人数 -> 存在する役職 の Map
        HashMap<Integer, HashSet<Role>> villageSizeRolesMap = new HashMap<>();
        villageSizeRolesMap.put(5, new HashSet<>(Arrays.asList(Role.WEREWOLF, Role.POSSESSED, Role.SEER, Role.VILLAGER)));
        villageSizeRolesMap.put(15, new HashSet<>(Arrays.asList(Role.WEREWOLF, Role.POSSESSED, Role.SEER, Role.BODYGUARD, Role.MEDIUM, Role.VILLAGER)));
        
        for (Map.Entry<Integer, HashSet<Role>> entry : villageSizeRolesMap.entrySet()) {
            int villageSize = entry.getKey();
            Set<Role> roles = entry.getValue();
            
            for (Role myRole : roles) {
                for (Role targetRole : roles) {
                    // 学習済みモデルが存在しない組み合わせを除外する。
                    if (!((myRole == Role.WEREWOLF || myRole == Role.POSSESSED || myRole == Role.SEER || myRole == Role.BODYGUARD || myRole == Role.MEDIUM) && myRole == targetRole)) {
                        JFastText jft = new JFastText();
                        String identifier = villageSize + "-" + myRole.toString() + "-" + targetRole.toString();
                        String fileName = "model/model-" + identifier + ".bin";
                        // simpleLog("Reading Model: " + fileName);
                        try {
                            jft.loadModel(LoadedModelMap.class.getResourceAsStream(fileName));
                        } catch (IOException e) {
                            log("例外です。。。");
                            e.printStackTrace();
                        }
                        modelMap.put(identifier, jft);
                        
                        // パターンごとのモデルを読み込む。
                        if (useModel_s02 && villageSize == 5) {
                            JFastText jft2 = new JFastText();
                            String identifier2 = villageSize + "-" + myRole.toString() + "-" + targetRole.toString() + "-s02";
                            String fileName2 = "model/model-" + identifier2 + ".bin";
                            // simpleLog("Reading Model: " + fileName);
                            try {
                                jft2.loadModel(LoadedModelMap.class.getResourceAsStream(fileName2));
                            } catch (IOException e) {
                                e.printStackTrace();
                            }
                            modelMap.put(identifier2, jft2);
                        }
                    }
                }
            }
        }
        
        // ストップウォッチ ストップ
        sw_init.stop();
    }
    
    /**
     * プレイヤーの人数と自分の役職と推定対象の役職と自称占い師の人数から，対応するモデルを返す。
     * たとえば，5人村で占い師が人狼を予測するモデルを得るには，getModel(5, Role.SEER, Role.WEREWOLF) とする。
     */
    public JFastText getModel(int villageSize, Role myRole, Role targetRole, int numberOfSeers) {
        String identifier = villageSize + "-" + myRole.toString() + "-" + targetRole.toString();
        if (useModel_s02 && villageSize == 5) {
            switch (numberOfSeers) {
                case 2:
                    identifier += "-s02";
                    // log("[OK] '-s02' model is being used: " + identifier);
                    break;
                case 1:
                case 3:
                default:
                    // 何もしない
                    break;
            }
        }
        return modelMap.get(identifier);
    }
    
}
