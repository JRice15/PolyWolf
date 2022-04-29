package jp.ac.tsukuba.s.s2020602.utils;

import org.aiwolf.common.data.Role;

import java.util.regex.Pattern;

/** デバッグをするときに限り log(String) メソッドで文字列の内容を出力するためのインターフェース． */
public interface DebugPrint {
    
    /** これが true だと，log の引数の内容を出力します． */
    boolean debug = true;
    
    /** debugがtrueのときに限り，動作確認用の文字列を出力します。カッコ内に呼び出し元のメソッドと行番号もプリントします。 */
    default void log(String str) {
        if (debug) {
            // System.out.print("log: "); // <- お好みで
            System.out.print(str);
            printPlace();
        }
    }
    
    /** 完全なスタックトレースを出力します。 */
    default void printFullStackTrace() {
        if (debug) {
            (new Throwable()).printStackTrace();
        }
    }
    
    /** どこで そのメソッドを呼んでいるかを印刷する */
    default void printPlace() {
        StackTraceElement[] st = (new Throwable()).getStackTrace();
        
        // log メソッドの 1 つ前の呼び出し元（st[2]）のクラス名とメソッド名と行番号
        String className = st[2].getClassName();
        String methodName = st[2].getMethodName();
        int line = st[2].getLineNumber();
        
        // パッケージ名を表示しないようにする．
        String[] path = className.split(Pattern.quote("."));
        String classSimpleName = path[path.length - 1];
        
        System.out.println(" (" + classSimpleName + "#" + methodName + ", line: " + line + ")");
    }
    
    /** debugがtrueのときに限り，動作確認用の文字列を出力します。 */
    default void simpleLog(String str) {
        if (debug) {
            // System.out.print("log: "); // <- お好みで
            System.out.println(str);
        }
    }
    
    default void simpleLogWithoutNewLine(String str) {
        if (debug) {
            System.out.print(str);
        }
    }
    
    // 役職の名前を1文字で出力する
    default String toKanji(Role role) {
        String kanji = "";
        switch (role) {
            case BODYGUARD:
                kanji = "B";
                break;
            case MEDIUM:
                kanji = "M";
                break;
            case POSSESSED:
                kanji = "P";
                break;
            case SEER:
                kanji = "S";
                break;
            case VILLAGER:
                kanji = "V";
                break;
            case WEREWOLF:
                kanji = "W";
                break;
            case FOX:
            case FREEMASON:
                kanji = "@";
                break;
            case ANY:
                kanji = "x";
                break;
        }
        return kanji;
    }
}
