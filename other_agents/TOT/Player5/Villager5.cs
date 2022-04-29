//
// Villager5.cs
//
// Copyright 2021 OTSUKI Takashi
// SPDX-License-Identifier: Apache-2.0
//

using AIWolf.Lib;
using System.Linq;

namespace TOT2021
{
    class Villager5 : BasePlayer5
    {
        public Villager5(MetaInfo metaInfo) : base(metaInfo) { }

        public override string Talk()
        {
            VoteCandidate = GetAgentsAssignedTo(Role.WEREWOLF).First();
            switch (Date)
            {
                case 1:
                    if (VoteCandidate != DeclaredVoteCandidate)
                    {
                        TalkVoting(VoteCandidate);
                        DeclaredVoteCandidate = VoteCandidate;
                    }
                    break;
                case 2:
                    if (VoteCandidate != DeclaredVoteCandidate)
                    {
                        TalkVoting(VoteCandidate);
                        var ally = SelectMin(Role.WEREWOLF, AliveOthers, VoteCandidate);
                        TalkVoteRequest(ally, VoteCandidate);
                        DeclaredVoteCandidate = VoteCandidate;
                    }
                    if (!IsPP)
                    {
                        IsPP = AliveOthers.Count == 2 && (IsCo(Role.WEREWOLF) || IsCo(Role.POSSESSED));
                        if (IsPP)
                        {
                            CancelAllTalk();
                            TalkCo(Role.WEREWOLF);
                            DeclaredVoteCandidate = Agent.NONE;
                        }
                    }
                    break;
                default:
                    break;
            }
            NextTurn();
            return DequeueTalk();
        }

        public override Agent Vote()
        {
            if (Date == 1)
            {
                if (!IsRevote)
                {
                    VoteReasonMap.Put(Me, VoteCandidate);
                    VoteCandidate = AdjustVote(VoteReasonMap, Me, 1.0);
                }
                else
                {
                    var vmap = new VoteReasonMap();
                    GameInfo.LatestVoteList.ToList().ForEach(v => vmap.Put(v.Agent, v.Target));
                    VoteCandidate = AdjustVote(vmap, Me, 1.0);
                }
            }
            IsRevote = true;
            return VoteCandidate;
        }

    }
}
