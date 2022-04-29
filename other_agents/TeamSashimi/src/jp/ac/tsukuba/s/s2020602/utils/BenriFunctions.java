package jp.ac.tsukuba.s.s2020602.utils;

import org.aiwolf.common.data.Role;
import org.aiwolf.common.data.Team;

import java.util.ArrayList;
import java.util.Collections;
import java.util.List;

public interface BenriFunctions {
    
    public static void main(String[] args) {
        // テスト
        List<String> list = new ArrayList<>();
        list.add("a");
        list.add("b");
        list.add("c");
        list.add("d");
        list.add("e");
        list.add("f");
        list.add("g");
        System.out.println(permutationsList(3, list));
        System.out.println(permutationsList(3, list).size());
    }
    
    /** 役職 eliminatedRole の人が追放／襲撃されたときに 役職 myRole の人に与えられる利得を返します。 */
    default double getPayoff(Role myRole, Role eliminatedRole) {
        int isVillagerTeam = (myRole.getTeam() == Team.VILLAGER ? 1 : -1);
        return getPayoff(isVillagerTeam, eliminatedRole);
    }
    
    /**
     * 役職 eliminatedRole の人が追放／襲撃されたときの利得を返します。
     * 利得を受け取る人が村人陣営なのか人狼陣営なのかは，isVillagerTeam を使って表現します。
     *
     * @param isVillagerTeam 自分（利得を受け取る人）が村人陣営に属するならば 1，人狼陣営に属するならば -1 にする。
     */
    default double getPayoff(int isVillagerTeam, Role eliminatedRole) {
        double payoffForVillagerTeam = 0;
        switch (eliminatedRole) {
            case BODYGUARD:
                payoffForVillagerTeam = -0.9;
                break;
            case MEDIUM:
                payoffForVillagerTeam = -0.6;
                break;
            case POSSESSED:
                payoffForVillagerTeam = 0.8;
                break;
            case SEER:
                payoffForVillagerTeam = -1.2;
                break;
            case VILLAGER:
                payoffForVillagerTeam = -0.3;
                break;
            case WEREWOLF:
                payoffForVillagerTeam = 2.0;
                break;
            default:
                payoffForVillagerTeam = 0;
        }
        return payoffForVillagerTeam * isVillagerTeam;
    }
    
    
    /** リストからランダムに選んで返す。 */
    default <T> T randomSelect(List<T> list) {
        if (list.isEmpty()) {
            return null;
        } else {
            return list.get((int) (Math.random() * list.size()));
        }
    }
    
    // 順列のためのメソッド
    
    /** リスト tail の先頭に要素 head を加えた新しいリスト（head :: tail）を返す。 */
    static <T> List<T> cons(T head, List<T> tail) {
        List<T> list = new ArrayList<>();
        list.add(head);
        list.addAll(tail);
        return list;
    }
    
    /** リスト list から要素 e を削除した新しいリストを返す。 */
    static <T> List<T> remove(T e, List<T> list) {
        List<T> newList = new ArrayList<>(list);
        newList.remove(e);
        return newList;
    }
    
    /** リスト list の中から n 個の要素を選ぶときの順列のリストを返します。 */
    static <E> List<List<E>> permutationsList(int n, List<E> list) {
        if (n <= 0) {
            return Collections.singletonList(Collections.emptyList());
        } else {
            List<List<E>> result = new ArrayList<>();
            for (E head : list) {
                for (List<E> tail : permutationsList(n - 1, remove(head, list))) {
                    result.add(cons(head, tail));
                }
            }
            return result;
        }
    }
    
}
