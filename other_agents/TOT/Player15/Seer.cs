//
// Seer.cs
//
// Copyright 2021 OTSUKI Takashi
// SPDX-License-Identifier: Apache-2.0
//

using AIWolf.Lib;
using System.Collections.Generic;
using System.Linq;

namespace TOT2021
{
    class Seer : Villager
    {
        int coDate;
        bool hasCo;
        int myDivinationHead;

        public Seer(MetaInfo metaInfo) : base(metaInfo) { }

        public override void Initialize(IGameInfo gameInfo, IGameSetting gameSetting)
        {
            base.Initialize(gameInfo, gameSetting);
            coDate = 3;
            hasCo = false;
            myDivinationHead = 0;
        }

        protected override void ChooseVoteCandidate0()
        {
            VoteCandidate = AliveOthers.OrderByDescending(a => VoteEval(a)).First();
            VoteReasonMap.Put(Me, VoteCandidate);
        }

        private double VoteEval(Agent agent) => GetProbOf(agent, Role.WEREWOLF) + 0.1 * GetProbOf(agent, Role.POSSESSED)
                + (IsWolf(agent) ? 1.0 : 0.0) + (IsHuman(agent) ? -1.0 : 0.0)
                + (IsFakeSeer(agent) ? 0.5 : 0.0) + (IsFakeMedium(agent) ? 0.5 : 0.0);

        bool FoundPossessed
        {
            get
            {
                var all = Others.Select(a => GetProbOf(a, Role.POSSESSED)).Sum();
                var alive = AliveOthers.Select(a => GetProbOf(a, Role.POSSESSED)).Sum();
                return alive > 0.5 * all || IsCo(Role.POSSESSED);
            }
        }

        public override string Talk()
        {
            if (GameInfo.AliveAgentList.Count <= 3)
            {
                if (!IsPP && FoundPossessed)
                {
                    IsPP = true;
                    TalkCo(Role.WEREWOLF);
                }
                return base.Talk();
            }
            if (!hasCo && (Date >= coDate || IsCo(Role.SEER) || FoundWolf))
            {
                TalkCo(Role.SEER);
                hasCo = true;
            }
            if (hasCo)
            {
                var nextHead = MyDivinations.Count;
                var divinations = new List<Judge>();
                for (var i = nextHead - 1; i >= myDivinationHead; i--)
                {
                    divinations.Add(MyDivinations[i]);
                }
                divinations.ForEach(j => TalkDivined(j.Target, j.Result));
                List<Content> contents = divinations.Select(j => DayContent(Me, j.Day, DivinedContent(Me, j.Target, j.Result))).ToList();
                contents.ForEach(c => EnqueueTalk(c));
                if (contents.Count() > 1)
                {
                    EnqueueTalk(AndContent(Me, contents.ToArray()));
                }
                myDivinationHead = nextHead;
            }
            return base.Talk();
        }

        public override Agent Divine() => GetGray(AliveOthers).OrderByDescending(a => DivineEval(a)).DefaultIfEmpty(Agent.NONE).First();

        private double DivineEval(Agent agent) => GetProbOf(agent, Role.WEREWOLF);
    }
}
