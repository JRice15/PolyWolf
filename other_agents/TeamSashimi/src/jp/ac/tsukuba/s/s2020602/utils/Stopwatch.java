package jp.ac.tsukuba.s.s2020602.utils;

/** 実行時間を計測するためのストップウォッチ */
public class Stopwatch implements DebugPrint {
    
    private long start = 0;
    
    private void startButton() {
        this.start = System.currentTimeMillis();
    }
    
    public void start() {
        // simpleLog(((new Throwable()).getStackTrace())[1].getMethodName() + " 開始");
        startButton();
    }
    
    private long stopButton() {
        long stop = System.currentTimeMillis();
        return (stop - this.start);
    }
    
    /** 100ミリ秒を超えると [[TIME OVER]] と表示します。 */
    public void stop() {
        long time = stopButton();
        if (time < 100) {
            simpleLog(((new Throwable()).getStackTrace())[1].getMethodName() + " takes " + time + " ms.");
        } else {
            // 100msをオーバーしたときは目立つようにしてあります。
            simpleLog("[[TIME OVER]] '" + ((new Throwable()).getStackTrace())[1].getMethodName() + "' takes " + time + " ms. [[TimeOverTimeOverTimeOverTimeOverTimeOverTimeOverTimeOverTimeOverTimeOverTimeOver]]");
        }
    }
    
}
