//
// TOTPlayer.cs
//
// Copyright 2021 OTSUKI Takashi
// SPDX-License-Identifier: Apache-2.0
//

using AIWolf.Lib;
using System.Linq;

namespace TOT2021
{
    public class TOTPlayer : IPlayer
    {
        IGameInfo gameInfo = default!;
        MetaInfo metaInfo;
        IPlayer player;

        public TOTPlayer()
        {
            metaInfo = new MetaInfo();
            player = new RoleAssignPlayer(metaInfo);
        }

        public string Name => "TOT";

        public Agent Attack()
        {
            return player.Attack();
        }

        public void DayStart()
        {
            player.DayStart();
        }

        public Agent Divine()
        {
            return player.Divine();
        }

        public void Finish()
        {
            metaInfo.Finish(gameInfo);

            var nAliveWolf = gameInfo.AliveAgentList.Where(a => gameInfo.RoleMap[a] == Role.WEREWOLF).Count();
            foreach (var e in gameInfo.RoleMap)
            {
                if ((e.Value == Role.WEREWOLF || e.Value == Role.POSSESSED) == (nAliveWolf > 0))
                {
                    metaInfo.IncrementWinCount(e.Key);
                }
            }
            player.Finish();
        }

        public Agent Guard()
        {
            return player.Guard();
        }

        public void Initialize(IGameInfo gameInfo, IGameSetting gameSetting)
        {
            metaInfo.Initialize(gameInfo);
            player.Initialize(gameInfo, gameSetting);
        }

        public string Talk()
        {
            return player.Talk();
        }

        public void Update(IGameInfo gameInfo)
        {
            this.gameInfo = gameInfo;
            metaInfo.Update(gameInfo);
            player.Update(gameInfo);
        }

        public Agent Vote()
        {
            return player.Vote();
        }

        public string Whisper()
        {
            return player.Whisper();
        }
    }
}
