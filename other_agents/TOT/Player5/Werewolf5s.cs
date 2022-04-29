//
// Werewolf5s.cs
//
// Copyright 2021 OTSUKI Takashi
// SPDX-License-Identifier: Apache-2.0
//

using AIWolf.Lib;
using System.Collections.Generic;
using System.Linq;

namespace TOT2021
{
    /// <summary>
    /// Werewolf for 5 agent village acting as a seer.
    /// </summary>
    class Werewolf5s : Werewolf5
    {
        BasePlayer5 innerSeer;
        MetaInfo fakeMetaInfo;
        Agent divinedHuman = Agent.NONE;
        Queue<IGameInfo> gameInfoList = new Queue<IGameInfo>();


        public Werewolf5s(MetaInfo metaInfo, MetaInfo fakeMetaInfo) : base(metaInfo, fakeMetaInfo)
        {
            this.fakeMetaInfo = fakeMetaInfo;
            innerSeer = new Seer5(fakeMetaInfo);
        }

        public override void Initialize(IGameInfo gameInfo, IGameSetting gameSetting)
        {
            base.Initialize(gameInfo, gameSetting);
            divinedHuman = Agent.NONE;
            gameInfoList.Clear();
            var fakeGameInfo = GetFakeGameInfo(gameInfo, Role.SEER, Judge.Empty);
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
            var possessed = GetAgentsAssignedTo(Role.POSSESSED).First();
            switch (Date)
            {
                case 1:
                    switch (Turn)
                    {
                        case 0:
                            TalkCo(Role.SEER);
                            break;
                        case 1:
                            TalkDivined(possessed, Species.HUMAN);
                            divinedHuman = possessed;
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
                            fakeGameInfo = GetFakeGameInfo(gameInfoList.Dequeue(), Role.SEER, new Judge(Date, Me, possessed, Species.HUMAN));
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
                    VoteCandidate = SelectMin(Role.POSSESSED, AliveOthers);
                    var ally = SelectMax(Role.POSSESSED, AliveOthers, VoteCandidate);
                    if (Turn == 0)
                    {
                        if (divinedHuman == ally)
                        {
                            TalkDivined(VoteCandidate, Species.WEREWOLF);
                        }
                        else
                        {
                            TalkDivined(ally, Species.HUMAN);
                        }
                    }
                    if (VoteCandidate != DeclaredVoteCandidate)
                    {
                        TalkVoting(VoteCandidate);
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
