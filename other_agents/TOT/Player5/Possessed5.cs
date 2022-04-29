//
// Possessed5.cs
//
// Copyright 2021 OTSUKI Takashi
// SPDX-License-Identifier: Apache-2.0
//

using AIWolf.Lib;
using System.Collections.Generic;
using System.Linq;

namespace TOT2021
{
    class Possessed5 : BasePlayer5
    {
        BasePlayer5 innerSeer;
        MetaInfo fakeMetaInfo;
        Agent divinedHuman = Agent.NONE;
        Queue<IGameInfo> gameInfoList = new Queue<IGameInfo>();

        public Possessed5(MetaInfo metaInfo, MetaInfo fakeMetaInfo) : base(metaInfo)
        {
            this.fakeMetaInfo = fakeMetaInfo;
            innerSeer = new Seer5(fakeMetaInfo);
        }

        public override void Initialize(IGameInfo gameInfo, IGameSetting gameSetting)
        {
            base.Initialize(gameInfo, gameSetting);
            divinedHuman = Agent.NONE;
            gameInfoList.Clear();
            IGameInfo fakeGameInfo = GetFakeGameInfo(GameInfo, Role.SEER, Judge.Empty);
            fakeMetaInfo.Initialize(fakeGameInfo);
            innerSeer.Initialize(fakeGameInfo, gameSetting);
        }

        public override void Update(IGameInfo gameInfo)
        {
            base.Update(gameInfo);
            if (Date > 0)
            {
                gameInfoList.Enqueue(new GameInfoModifier(gameInfo));
            }
            else
            {
                IGameInfo fakeGameInfo = GetFakeGameInfo(gameInfo, Role.SEER, Judge.Empty);
                fakeMetaInfo.Update(fakeGameInfo);
                innerSeer.Update(fakeGameInfo);
            }
        }

        public override string Talk()
        {
            Agent werewolf = GetAgentsAssignedTo(Role.WEREWOLF).First();
            switch (Date)
            {
                case 1:
                    switch (Turn)
                    {
                        case 0:
                            TalkCo(Role.SEER);
                            break;
                        case 1:
                            TalkDivined(werewolf, Species.HUMAN);
                            divinedHuman = werewolf;
                            var fakeDivination = new Judge(Date, Me, divinedHuman, Species.HUMAN);
                            var fakeGameInfo = GetFakeGameInfo(gameInfoList.Dequeue(), Role.SEER, fakeDivination);
                            fakeMetaInfo.Update(fakeGameInfo);
                            innerSeer.Update(fakeGameInfo);
                            innerSeer.DayStart();
                            fakeGameInfo = GetFakeGameInfo(gameInfoList.Dequeue(), Role.SEER, fakeDivination);
                            fakeMetaInfo.Update(fakeGameInfo);
                            innerSeer.Update(fakeGameInfo);
                            _ = innerSeer.Talk();
                            fakeGameInfo = GetFakeGameInfo(gameInfoList.Dequeue(), Role.SEER, fakeDivination);
                            fakeMetaInfo.Update(fakeGameInfo);
                            innerSeer.Update(fakeGameInfo);
                            _ = innerSeer.Talk();
                            break;
                        default:
                            fakeGameInfo = GetFakeGameInfo(gameInfoList.Dequeue(), Role.SEER, new Judge(Date, Me, werewolf, Species.HUMAN));
                            fakeMetaInfo.Update(fakeGameInfo);
                            innerSeer.Update(fakeGameInfo);
                            _ = innerSeer.Talk();
                            VoteCandidate = innerSeer.GetAgentsAssignedTo(Role.WEREWOLF, divinedHuman).First();
                            if (VoteCandidate != DeclaredVoteCandidate)
                            {
                                TalkVoting(VoteCandidate);
                                DeclaredVoteCandidate = VoteCandidate;
                            }
                            break;
                    }
                    break;
                case 2:
                    VoteCandidate = SelectMin(Role.WEREWOLF, AliveOthers, werewolf);
                    if (Turn == 0)
                    {
                        TalkDivined(VoteCandidate, Species.WEREWOLF);
                    }
                    if (VoteCandidate != DeclaredVoteCandidate)
                    {
                        TalkVoting(VoteCandidate);
                        TalkVoteRequest(werewolf, VoteCandidate);
                        DeclaredVoteCandidate = VoteCandidate;
                    }
                    if (!IsPP)
                    {
                        IsPP = AliveOthers.Count == 2 && (GetRoleCount(Role.POSSESSED) == 1 || GetPpAbility(werewolf) || IsCo(Role.WEREWOLF) || IsCo(Role.POSSESSED));
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
            Agent werewolf = GetAgentsAssignedTo(Role.WEREWOLF).First();
            VoteCandidate = SelectMin(Role.WEREWOLF, AliveOthers, werewolf);
            if (!IsRevote)
            {
                VoteReasonMap.Put(Me, VoteCandidate);
                VoteCandidate = AdjustVote(VoteReasonMap, werewolf, 1.0);
            }
            else
            {
                var vmap = new VoteReasonMap();
                GameInfo.LatestVoteList.ToList().ForEach(v => vmap.Put(v.Agent, v.Target));
                VoteCandidate = AdjustVote(vmap, werewolf, 1.0);
            }
            IsRevote = true;
            return VoteCandidate;
        }

    }
}
