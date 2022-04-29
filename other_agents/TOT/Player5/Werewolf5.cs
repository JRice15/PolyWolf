//
// Werewolf5.cs
//
// Copyright 2021 OTSUKI Takashi
// SPDX-License-Identifier: Apache-2.0
//

using AIWolf.Lib;
using System.Linq;

namespace TOT2021
{
    class Werewolf5 : BasePlayer5
    {
        BasePlayer5 innerVillager;
        MetaInfo fakeMetaInfo;

        public Werewolf5(MetaInfo metaInfo, MetaInfo fakeMetaInfo) : base(metaInfo)
        {
            this.fakeMetaInfo = fakeMetaInfo;
            innerVillager = new Villager5(fakeMetaInfo);
        }

        public override void Initialize(IGameInfo gameInfo, IGameSetting gameSetting)
        {
            base.Initialize(gameInfo, gameSetting);
            var fakeGameInfo = GetFakeGameInfo(gameInfo, Role.VILLAGER, Judge.Empty);
            fakeMetaInfo.Initialize(fakeGameInfo);
            innerVillager.Initialize(fakeGameInfo, gameSetting);
        }

        public override void Update(IGameInfo gameInfo)
        {
            base.Update(gameInfo);
            var fakeGameInfo = GetFakeGameInfo(gameInfo, Role.VILLAGER, Judge.Empty);
            fakeMetaInfo.Update(fakeGameInfo);
            innerVillager.Update(fakeGameInfo);
        }

        public override string Talk()
        {
            switch (Date)
            {
                case 1:
                    VoteCandidate = innerVillager.GetAgentsAssignedTo(Role.WEREWOLF).First();
                    if (VoteCandidate != DeclaredVoteCandidate)
                    {
                        TalkVoting(VoteCandidate);
                        DeclaredVoteCandidate = VoteCandidate;
                    }
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

        public override Agent Vote()
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
            IsRevote = true;
            return VoteCandidate;
        }

        public override Agent Attack() => SelectMin(Role.POSSESSED, AliveOthers);

    }
}
