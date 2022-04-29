//
// RoleAssignPlayer.cs
//
// Copyright 2021 OTSUKI Takashi
// SPDX-License-Identifier: Apache-2.0
//

using AIWolf.Lib;
using System;

namespace TOT2021
{
    class RoleAssignPlayer : IPlayer
    {
        IPlayer villager;
        IPlayer seer;
        IPlayer medium;
        IPlayer bodyguard;
        IPlayer possessed;
        IPlayer werewolf;

        IPlayer villager5;
        IPlayer seer5;
        IPlayer possessed5;
        IPlayer werewolf5;
        IPlayer werewolf5s;
        IPlayer werewolf5x;
        IPlayer werewolf5y;

        IPlayer player = default!;

        MetaInfo metaInfo;
        MetaInfo fakeMetaInfo;

        int winCountAsWolf;
        int myLastWinCount;
        Agent me = Agent.NONE;
        Role myRole;
        int werewolf5Mode;
        Random rand = new Random();

        public RoleAssignPlayer(MetaInfo metaInfo)
        {
            this.metaInfo = metaInfo;
            fakeMetaInfo = new MetaInfo();

            villager = new Villager(metaInfo);
            seer = new Seer(metaInfo);
            medium = new Medium(metaInfo);
            bodyguard = new Bodyguard(metaInfo);
            possessed = new Possessed(metaInfo, fakeMetaInfo);
            werewolf = new Werewolf(metaInfo, fakeMetaInfo);

            villager5 = new Villager5(metaInfo);
            seer5 = new Seer5(metaInfo);
            possessed5 = new Possessed5(metaInfo, fakeMetaInfo);
            werewolf5 = new Werewolf5(metaInfo, fakeMetaInfo);
            werewolf5s = new Werewolf5s(metaInfo, fakeMetaInfo);
            werewolf5x = new Werewolf5s(metaInfo, fakeMetaInfo);
            werewolf5y = new Werewolf5y(metaInfo, fakeMetaInfo);
        }

        public string Name => "RoleAssignPlayer";

        public void Update(IGameInfo gameInfo)
        {
            player.Update(gameInfo);
        }

        public void Initialize(IGameInfo gameInfo, IGameSetting gameSetting)
        {
            var playerNum = gameSetting.PlayerNum;
            me = gameInfo.Agent;
            myRole = gameInfo.Role;
            metaInfo.IncrementRoleCount(myRole);
            switch (myRole)
            {
                case Role.VILLAGER:
                    player = playerNum == 5 ? villager5 : villager;
                    break;
                case Role.SEER:
                    player = playerNum == 5 ? seer5 : seer;
                    break;
                case Role.MEDIUM:
                    player = medium;
                    break;
                case Role.BODYGUARD:
                    player = bodyguard;
                    break;
                case Role.POSSESSED:
                    player = playerNum == 5 ? possessed5 : possessed;
                    break;
                case Role.WEREWOLF:
                    if (playerNum == 5)
                    {
                        if (metaInfo.GetRoleCount(Role.WEREWOLF) == 6)
                        {
                            if (winCountAsWolf < 2)
                            {
                                werewolf5Mode = 1;
                            }
                            else
                            {
                                werewolf5Mode = 2;
                            }
                        }
                        switch (werewolf5Mode)
                        {
                            case 0:
                                player = rand.NextDouble() < 0.5 ? werewolf5x : werewolf5y;
                                break;
                            case 1:
                                if (metaInfo.GameCount < 40)
                                {
                                    player = rand.NextDouble() < 0.5 ? werewolf5x : werewolf5y;
                                }
                                else if (metaInfo.GameCount < 80)
                                {
                                    player = werewolf5s;
                                }
                                else
                                {
                                    player = werewolf5;
                                }
                                break;
                            case 2:
                                player = rand.NextDouble() < 0.5 ? werewolf5 : werewolf5s;
                                break;
                            default:
                                break;
                        }
                    }
                    else
                    {
                        player = werewolf;
                    }
                    break;
                default:
                    player = villager;
                    break;
            }
            player.Initialize(gameInfo, gameSetting);
            myLastWinCount = metaInfo.GetWinCount(me);
        }

        public void DayStart()
        {
            player.DayStart();
        }

        public string Talk()
        {
            return player.Talk();
        }

        public string Whisper()
        {
            return player.Whisper();
        }

        public Agent Vote()
        {
            return player.Vote();
        }

        public Agent Attack()
        {
            return player.Attack();
        }

        public Agent Divine()
        {
            return player.Divine();
        }

        public Agent Guard()
        {
            return player.Guard();
        }

        public void Finish()
        {
            player.Finish();
            if (myRole == Role.WEREWOLF)
            {
                winCountAsWolf += metaInfo.GetWinCount(me) - myLastWinCount;
            }
        }
    }
}
