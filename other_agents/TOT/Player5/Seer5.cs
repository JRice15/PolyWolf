//
// Seer5.cs
//
// Copyright 2021 OTSUKI Takashi
// SPDX-License-Identifier: Apache-2.0
//

using AIWolf.Lib;
using System.Linq;

namespace TOT2021
{
    class Seer5 : BasePlayer5
    {
        public Seer5(MetaInfo metaInfo) : base(metaInfo) { }

        public override string Talk()
        {
            switch (Date)
            {
                case 1:
                    VoteCandidate = GetAgentsAssignedTo(Role.WEREWOLF).First();
                    switch (Turn)
                    {
                        case 0:
                            TalkCo(Role.SEER);
                            break;
                        case 1:
                            var divination = GetMyDivinationOnDay(1);
                            if (divination != Judge.Empty)
                            {
                                TalkDivined(divination.Target, divination.Result);
                            }
                            break;
                        default:
                            if (VoteCandidate != DeclaredVoteCandidate)
                            {
                                TalkVoting(VoteCandidate);
                                DeclaredVoteCandidate = VoteCandidate;
                            }
                            break;
                    }
                    break;
                case 2:
                    VoteCandidate = SelectMax(Role.WEREWOLF, AliveOthers);
                    switch (Turn)
                    {
                        case 0:
                            var divination = GetMyDivinationOnDay(2);
                            if (divination != Judge.Empty)
                            {
                                TalkDivined(divination.Target, divination.Result);
                            }
                            break;
                        default:
                            if (VoteCandidate != DeclaredVoteCandidate)
                            {
                                TalkVoting(VoteCandidate);
                                var human = SelectMin(Role.WEREWOLF, AliveOthers, VoteCandidate);
                                TalkVoteRequest(human, VoteCandidate);
                                DeclaredVoteCandidate = VoteCandidate;
                            }
                            break;
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

        public override Agent Divine()
        {
            return RandomSelect(GetGray(AliveOthers));
        }
    }
}
