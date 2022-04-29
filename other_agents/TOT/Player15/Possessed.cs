//
// Possessed.cs
//
// Copyright 2021 OTSUKI Takashi
// SPDX-License-Identifier: Apache-2.0
//

using AIWolf.Lib;
using System.Collections.Generic;
using System.Linq;

namespace TOT2021
{
    class Possessed : BasePlayer
    {
        BasePlayer innerPlayer = default!;
        Judge fakeDivination = Judge.Empty;
        MetaInfo fakeMetaInfo;
        List<Agent> divinedList = new List<Agent>();

        public Possessed(MetaInfo metaInfo, MetaInfo fakeMetaInfo) : base(metaInfo) => this.fakeMetaInfo = fakeMetaInfo;

        public override void Initialize(IGameInfo gameInfo, IGameSetting gameSetting)
        {
            base.Initialize(gameInfo, gameSetting);

            fakeDivination = Judge.Empty;
            innerPlayer = new Seer(fakeMetaInfo);
            IGameInfo fakeGameInfo = GetFakeGameInfo(gameInfo);
            fakeMetaInfo.Initialize(fakeGameInfo);
            innerPlayer.Initialize(fakeGameInfo, gameSetting);
            divinedList.Clear();
        }

        private IGameInfo GetFakeGameInfo(IGameInfo gameInfo)
        {
            GameInfoModifier gim = new GameInfoModifier(gameInfo);
            gim.SetFakeRole(Role.SEER);
            if (fakeDivination != Judge.Empty)
            {
                gim.SetDivineResult(new Judge(Date, fakeDivination.Agent, fakeDivination.Target, fakeDivination.Result));
            }
            return gim;
        }

        public override void Update(IGameInfo gameInfo)
        {
            bool isFakeDivineTime = Date > -1 && gameInfo.Day == Date + 1;
            base.Update(gameInfo);

            if (isFakeDivineTime)
            {
                fakeDivination = NextJudge();
            }

            IGameInfo fakeGameInfo = GetFakeGameInfo(gameInfo);
            fakeMetaInfo.Update(fakeGameInfo);
            innerPlayer.Update(fakeGameInfo);
        }

        private Judge NextJudge()
        {
            var candidates = AliveOthers.Where(a => !divinedList.Contains(a));
            if (candidates.Count() == 0)
            {
                return Judge.Empty;
            }
            Judge next = Date switch
            {
                1 => new Judge(Date, Me, SelectMin(Role.WEREWOLF, candidates), Species.WEREWOLF),
                2 => new Judge(Date, Me, SelectMax(Role.WEREWOLF, candidates), Species.HUMAN),
                3 => new Judge(Date, Me, SelectMin(Role.WEREWOLF, candidates), Species.WEREWOLF),
                _ => new Judge(Date, Me, SelectMax(Role.WEREWOLF, candidates), Species.HUMAN),
            };
            divinedList.Add(next.Target);
            return next;
        }

        public override void DayStart()
        {
            base.DayStart();
            innerPlayer.DayStart();
        }

        public override string Talk()
        {
            if (GameInfo.AliveAgentList.Count <= 3)
            {
                if (!IsPP)
                {
                    IsPP = true;
                    TalkCo(Role.WEREWOLF);
                }
                return base.Talk();
            }
            else
            {
                return innerPlayer.Talk();
            }
        }

        protected override void ChooseVoteCandidate(bool isLast)
        {
            VoteCandidate = innerPlayer.Vote();
            if (isLast)
            {
                if (GameInfo.AliveAgentList.Count <= 3)
                {
                    VoteCandidate = SelectMin(Role.WEREWOLF, AliveOthers);
                }
                else
                {
                    if (!innerPlayer.GetWolf(AliveOthers).Contains(VoteCandidate))
                    {
                        var wolf = SelectMax(Role.WEREWOLF, AliveOthers);
                        var target = VoteReasonMap.GetTarget(wolf);
                        VoteCandidate = target == Agent.NONE || IsDead(target) ? SelectMin(Role.WEREWOLF, AliveOthers) : target;
                    }
                }
            }
        }

    }
}
