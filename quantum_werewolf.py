import pandas as pd
import numpy as np
import itertools
import random
import os

num_of_players=int(input("プレイ人数を入力してください:"))
seq=["ド人狼","占い師","市民","市民"]
if num_of_players<6:
    while len(seq)<num_of_players:
        seq.append("市民")
else:
    while len(seq)<num_of_players-1:
        seq.append("市民")
    seq.append("人狼")
player_list=[]
for i in range(1,len(seq)+1):
    player_list.append("player%s" % str(i))
#print(seq)
#print(player_list)

dead_list=[]

def prob_df_show(df):
    prob_df=pd.DataFrame(columns=['人狼','市民','死亡'])
    for i in range(1,num_of_players+1):
        player="player%s" % str(i)
        dead_player="dead%s" % str(i)
        prob_dead=((df[dead_player]==True).sum())/len(df)
        prob_wolf=0.0
        if len(df)-((df[dead_player]==True).sum())>0:
            prob_wolf=((((df[player]=="ド人狼")|(df[player]=="人狼"))&(df[dead_player]==False)).sum())/(len(df)-((df[dead_player]==True).sum()))
        prob_human=0.0
        if len(df)-((df[dead_player]==True).sum())>0:
            prob_human=((((df[player]=="市民")|(df[player]=="占い師"))&(df[dead_player]==False)).sum())/(len(df)-((df[dead_player]==True).sum()))
        temp_df=pd.Series([prob_wolf,prob_human,prob_dead],index=prob_df.columns,name=player)
        prob_df=prob_df.append(temp_df)
        if prob_dead==1.0:
            dead_list.append(str(i))
    print("<確率表>")
    print(prob_df)
    if prob_df["死亡"].sum()>=num_of_players-1:
        return True
    elif prob_df["人狼"].sum()==0.0:
        return True
    elif prob_df["市民"].sum()==0.0:
        return True
    else:
        return False



df=pd.DataFrame(list(itertools.permutations(seq)),columns=player_list)
for i in range(1,len(seq)+1):
    dead_player="dead%s" % str(i)
    df[dead_player]=False

daycount=0
while len(df)>1:
    daycount+=1
    
    #確率表を表示する
    if prob_df_show(df):
        break
    
    print("")
    print("<%s日目 昼>" % str(daycount))
    
    for i in range(1,num_of_players+1):
        player="player%s" % str(i)
        dead_player="dead%s" % str(i)

        if ((((df[player]=="占い師"))&(df[dead_player]==False)).sum())>0:
            #占い師フェーズ
            #占う相手を指定
            #指定された相手の役職をランダムで決める
            #それ以外のパターンを削除
            print("%s さんの占い師フェーズです。占う人の番号を入力してください" % player)
            while True:
                fortuned_player_num=input()
                if fortuned_player_num in dead_list:
                    print("そのplayerはすでに死亡しています。別のplayerを選択してください。")
                elif ("player%s" % fortuned_player_num) in player_list:
                    break
                else:
                    print("プレイヤーの数字を入力してください")
            fortuned_player="player%s" % fortuned_player_num
            dead_fortuned_player="dead%s" % fortuned_player_num
            fortuned_df=df.query('%s == False and %s == "占い師"' % (dead_fortuned_player,player))[fortuned_player]
            #確率的に決定 decided_position
            if len(fortuned_df)>0:
                decided_position=fortuned_df.iloc[random.randrange(len(fortuned_df)),]
                cond_state='%s != "占い師" or %s == "%s"' % (player,fortuned_player,decided_position)
                df.query(cond_state,inplace=True)
                print("占いの結果、player%s さんは%s でした"% (fortuned_player_num,decided_position))
            else:
                decided_position=df.query('%s == "占い師"' % (player))[fortuned_player].iloc[0,]
                print("占いの結果、player%s さんは%s でした"% (fortuned_player_num,decided_position))
            
            #debug
            #print(df)

    if prob_df_show(df):
        break

    print("")
    print("<%s日目 夜（処刑）>" % str(daycount))
    
    while True:
        executed_player_num=input("処刑するプレイヤーを選んでください:")
        if executed_player_num in dead_list:
            print("そのplayerはすでに死亡しています。別のplayerを選択してください。")
        elif ("player%s" % executed_player_num) in player_list:
            break
        else:
           print("プレイヤーの数字を入力してください")
    executed_player="player%s" % executed_player_num
    executed_dead_player="dead%s" % executed_player_num
    #死んでいたパターンを削除
    cond_state='%s == False' % executed_dead_player
    df.query(cond_state,inplace=True)
    #print(df)
    #全て死亡
    executed_df=df[executed_player]
    executed_decided_position=executed_df.iloc[random.randrange(len(executed_df)),]
    print("%sは処刑され、%sに確率が収束しました。"% (executed_player,executed_decided_position))
    cond_state='%s == "%s"' % (executed_player,executed_decided_position)
    df.query(cond_state,inplace=True)
    df[executed_dead_player]=True

    

    if prob_df_show(df):
        break

    print("")
    print("<%s日目 夜（襲撃）>" % str(daycount))

    for i in range(1,num_of_players+1):
        player="player%s" % str(i)
        dead_player="dead%s" % str(i)
        #人狼の確率があって、死んでいない場合
        if ((((df[player]=="ド人狼")|(df[player]=="人狼"))&(df[dead_player]==False)).sum())>0:
            #人狼フェーズ
            #指定された相手にdeadフラグを立て、人狼deadのセルを消去
            #殺す相手を指定
            print("%s さんの人狼フェーズです。殺す人の番号を入力してください" % player)
            while True:
                killed_player_num=input()
                if killed_player_num in dead_list:
                    print("そのplayerはすでに死亡しています。別のplayerを選択してください。")
                elif killed_player_num==str(i):
                    print("自分自身を殺す相手に指定することはできません。自分以外のplayerを選択してください")
                elif ("player%s" % killed_player_num) in player_list:
                    break
                else:
                    print("プレイヤーの数字を入力してください")
            killed_player="player%s" % killed_player_num
            killed_dead_player="dead%s" % killed_player_num
            
            #自分がドミナント人狼である場合は、相手が人狼である場合を削除して、人狼でない所にdeadフラグを立てる
            cond_state='%s != "ド人狼" or %s != "人狼"' % (player,killed_player)
            df.query(cond_state,inplace=True)
            df.loc[df[player]=="ド人狼",killed_dead_player]=True
            #自分が人狼で、すでにその世界線でドミナント人狼が志望している場合は、その相手にdeadフラグを立てる
            for j in range(1,num_of_players+1):
                dominant_player="player%s" % str(j)
                dominant_dead_player="dead%s" % str(j)
                df.loc[(df[player]=="人狼")&(df[dominant_player]=="ド人狼")&(df[dominant_dead_player]==True),killed_dead_player]=True
            #debug
            #print(df)

print("<ゲーム終了> 陣営が収束しました。")
print("残ったパターンは以下のようになります")
print(df)