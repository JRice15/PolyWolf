//
// Villager.cs
//
// Copyright 2021 OTSUKI Takashi
// SPDX-License-Identifier: Apache-2.0
//

using AIWolf.Lib;
using System;
using System.Linq;

namespace TOT2021
{
    class Villager : BasePlayer
    {
        public Villager(MetaInfo metaInfo) : base(metaInfo) { }

        public override void DayStart() => base.DayStart();

        protected virtual void ChooseVoteCandidate0()
        {
            VoteCandidate = AliveOthers.OrderByDescending(a => VoteEval1(a)).First();
            VoteReasonMap.Put(Me, VoteCandidate);
            if (VoteReasonMap.GetVoteCount(VoteCandidate) < AliveOthers.Count * 0.5)
            {
                VoteCandidate = AliveOthers.OrderByDescending(a => VoteEval2(a)).First();
                VoteReasonMap.Put(Me, VoteCandidate);
            }
        }

        protected override void ChooseVoteCandidate(bool isLast)
        {
            ChooseVoteCandidate0();

            if (isLast)
            {
                if (IsRevote)
                {
                    var vmap = new VoteReasonMap();
                    GameInfo.LatestVoteList.ToList().ForEach(v => vmap.Put(v.Agent, v.Target));
                    VoteCandidate = AdjustVote(vmap, Me, 0.5);
                }
                else
                {
                    VoteReasonMap.Put(Me, VoteCandidate);
                    VoteCandidate = AdjustVote(VoteReasonMap, Me, 0.5);
                }
            }
            else
            {
                if (Turn > 1)
                {
                    if (IsLikeWolf(VoteCandidate))
                    {
                        if (VoteCandidate != DeclaredWolf)
                        {
                            CancelEstimate(DeclaredWolf);
                            TalkEstimate(VoteCandidate, Role.WEREWOLF);
                            DeclaredWolf = VoteCandidate;
                        }
                    }
                }
                else
                {
                    VoteCandidate = Agent.NONE;
                }
            }
        }

        double VoteEval1(Agent agent) => VoteReasonMap.GetVoteCount(agent) + GetProbOf(agent, Role.WEREWOLF);

        double VoteEval2(Agent agent) => GetProbOf(agent, Role.WEREWOLF) + 0.1 * GetProbOf(agent, Role.POSSESSED)
            + (IsWolf(agent) ? 1.0 : 0.0) + (IsHuman(agent) ? -1.0 : 0.0)
            + (IsFakeSeer(agent) ? 0.5 : 0.0) + (IsFakeMedium(agent) ? 0.5 : 0.0);

        public override string Whisper() => throw new NotImplementedException();

        public override Agent Attack() => throw new NotImplementedException();

        public override Agent Divine() => throw new NotImplementedException();

        public override Agent Guard() => throw new NotImplementedException();

    }
}
