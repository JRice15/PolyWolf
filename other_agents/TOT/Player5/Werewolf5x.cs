//
// Werewolf5x.cs
//
// Copyright 2021 OTSUKI Takashi
// SPDX-License-Identifier: Apache-2.0
//

using AIWolf.Lib;

namespace TOT2021
{
    class Werewolf5x : Werewolf5
    {
        public Werewolf5x(MetaInfo metaInfo, MetaInfo fakeMetaInfo) : base(metaInfo, fakeMetaInfo) { }

        public override string Talk()
        {
            switch (Date)
            {
                case 1:
                    VoteCandidate = SelectMax(Role.VILLAGER, GetAgentsAssignedTo(Role.VILLAGER));
                    break;
                case 2:
                    VoteCandidate = SelectMin(Role.POSSESSED, AliveOthers);
                    if (VoteCandidate != DeclaredVoteCandidate)
                    {
                        TalkVoting(VoteCandidate);
                        var ally = SelectMax(Role.POSSESSED, AliveOthers, VoteCandidate);
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

    }
}
