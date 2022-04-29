//
// Werewolf.cs
//
// Copyright 2021 OTSUKI Takashi
// SPDX-License-Identifier: Apache-2.0
//

using AIWolf.Lib;
using System;
using System.Collections.Generic;
using System.Linq;

namespace TOT2021
{
    class Werewolf : BasePlayer
    {
        Role fakeRole;
        Agent attackVoteCandidate = Agent.NONE;
        Agent declaredAttackVoteCandidate = Agent.NONE;
        int whisperListHead;
        Queue<Content> whisperQueue = new Queue<Content>();
        Dictionary<Agent, Role> ourComingoutMap = new Dictionary<Agent, Role>();
        AttackVoteReasonMap attackVoteReasonMap = new AttackVoteReasonMap();
        BasePlayer innerPlayer = default!;
        IGameSetting gameSetting = default!;
        IGameInfo initialGameInfo = default!;
        Agent possessed = Agent.NONE;
        Agent declaredPossessed = Agent.NONE;
        Agent fakeDivineTarget = Agent.NONE;
        Species fakeResult;
        MetaInfo fakeMetaInfo;

        public Werewolf(MetaInfo metaInfo, MetaInfo fakeMetaInfo) : base(metaInfo) => this.fakeMetaInfo = fakeMetaInfo;

        public override void Initialize(IGameInfo gameInfo, IGameSetting gameSetting)
        {
            base.Initialize(gameInfo, gameSetting);
            initialGameInfo = gameInfo;
            this.gameSetting = gameSetting;

            whisperQueue.Clear();
            ourComingoutMap.Clear();
            attackVoteReasonMap.Clear();
            possessed = Agent.NONE;
            fakeDivineTarget = Agent.NONE;
            fakeResult = Species.UNC;
            fakeRole = new List<Role>() { Role.VILLAGER, Role.SEER, Role.MEDIUM }.Shuffle()[0];
            SetupFakeRole(fakeRole);
        }

        void SetupFakeRole(Role fakeRole)
        {
            switch (fakeRole)
            {
                case Role.SEER:
                    innerPlayer = new Seer(fakeMetaInfo);
                    break;
                case Role.MEDIUM:
                    innerPlayer = new Medium(fakeMetaInfo);
                    break;
                default:
                    innerPlayer = new Villager(fakeMetaInfo);
                    break;
            }
            IGameInfo fakeGameInfo = GetFakeGameInfo(initialGameInfo);
            fakeMetaInfo.Initialize(fakeGameInfo);
            innerPlayer.Initialize(fakeGameInfo, gameSetting);
            EnqueueWhisper(CoContent(Me, Me, fakeRole));
        }

#nullable disable
        private IGameInfo GetFakeGameInfo(IGameInfo gameInfo)
        {
            GameInfoModifier gim = new GameInfoModifier(gameInfo);
            gim.SetFakeRole(fakeRole);
            switch (fakeRole)
            {
                case Role.SEER:
                    if (fakeDivineTarget != Agent.NONE)
                    {
                        var fakeJudge = new Judge(gameInfo.Day, Me, fakeDivineTarget, fakeResult);
                        gim.SetDivineResult(fakeJudge);
                    }
                    break;
                case Role.MEDIUM:
                    var executed = gameInfo.ExecutedAgent;
                    if (executed != null)
                    {
                        var fakeJudge = new Judge(gameInfo.Day, Me, executed, fakeResult);
                        gim.SetMediumResult(fakeJudge);
                    }
                    break;
                default:
                    break;
            }
            return gim;
        }
#nullable restore

        public override void Update(IGameInfo gameInfo)
        {
            bool isFakeDivineTime = Date > -1 && gameInfo.Day == Date + 1;
            base.Update(gameInfo);

            if (isFakeDivineTime)
            {
                fakeDivineTarget = fakeRole == Role.SEER ? innerPlayer.Divine() : Agent.NONE;
                fakeResult = NextJudge();
            }
            IGameInfo fakeGameInfo = GetFakeGameInfo(gameInfo);
            fakeMetaInfo.Update(fakeGameInfo);
            innerPlayer.Update(fakeGameInfo);

            GetWolf(gameInfo.AgentList).ForEach(a => innerPlayer.OverwriteProbOf(a, Role.WEREWOLF, 0.0));

            ProcessWhisper();

            List<Agent> fakeJudges = GetAlive(FakeSeers);
            fakeJudges.AddRange(GetAlive(FakeMediums));
            fakeJudges = fakeJudges.Where(a => !IsWolf(a)).ToList();
            if (fakeJudges.Count != 0)
            {
                possessed = SelectMax(Role.POSSESSED, fakeJudges);
                innerPlayer.OverwriteProbOf(possessed, Role.WEREWOLF, 0.0);

                if (possessed != declaredPossessed)
                {
                    EnqueueWhisper(EstimateContent(Me, possessed, Role.POSSESSED));
                    declaredPossessed = possessed;
                }
            }
            else
            {
                possessed = Agent.NONE;
            }
        }

        private Species NextJudge()
        {
            var nWolves = innerPlayer.GetWolf(GameInfo.AgentList).Count;
            var remain = gameSetting.RoleNumMap[Role.WEREWOLF] - 1 - nWolves;
            return remain > 0 && Random.NextDouble() < 0.5 ? Species.WEREWOLF : Species.HUMAN;
        }

        void ProcessWhisper()
        {
            for (var i = whisperListHead; i < GameInfo.WhisperList.Count; i++)
            {
                var whisper = GameInfo.WhisperList[i];
                var whisperer = whisper.Agent;
                if (whisperer == Me)
                {
                    continue;
                }
                var content = new Content(whisper.Text);
                if (content.Subject == Agent.NONE)
                {
                    content = ReplaceSubject(content, whisperer);
                }
                ParseWhisper(content);
            }
            whisperListHead = GameInfo.WhisperList.Count;
        }

        void ParseWhisper(Content content)
        {
            if (EstimateReasonMap.Put(content) || attackVoteReasonMap.Put(content))
            {
                return;
            }
            switch (content.Topic)
            {
                case Topic.COMINGOUT:
                    ourComingoutMap[content.Subject] = content.Role;
                    return;
                default:
                    break;
            }
        }

        public override void DayStart()
        {
            base.DayStart();
            innerPlayer.DayStart();
            attackVoteCandidate = Agent.NONE;
            declaredAttackVoteCandidate = Agent.NONE;
            possessed = Agent.NONE;
            declaredPossessed = Agent.NONE;
            whisperListHead = 0;
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
            else
            {
                return innerPlayer.Talk();
            }
        }

        bool FoundPossessed
        {
            get
            {
                double all = Others.Select(a => GetProbOf(a, Role.POSSESSED)).Sum();
                double alive = AliveOthers.Select(a => GetProbOf(a, Role.POSSESSED)).Sum();
                return alive > 0.5 * all || IsCo(Role.POSSESSED) || IsCo(Role.WEREWOLF);
            }
        }

        Agent ChooseAttackVoteCandidate() => GetHuman(AliveOthers).OrderByDescending(a => AttackEval(a)).First();

        double AttackEval(Agent agent) => 0.2 * GetProbOf(agent, Role.SEER)
                    + 0.1 * (Exists(Role.BODYGUARD) ? GetProbOf(agent, Role.BODYGUARD) : 0.0)
                    + 0.1 * (Exists(Role.MEDIUM) ? GetProbOf(agent, Role.MEDIUM) : 0.0)
                    - GetProbOf(agent, Role.POSSESSED) + (agent == possessed ? -1.0 : 0.0)
                    + 3 * GetWinCount(agent) / (GameCount + 0.01);

        public override Agent Attack() => ChooseAttackVoteCandidate();

        public override string Whisper()
        {
            if (Date == 0)
            {
                var oldFakeRole = fakeRole;
                var fakeRoles = ourComingoutMap.Values;
                if (fakeRoles.Count > 0)
                {
                    if (!fakeRoles.Contains(Role.SEER))
                    {
                        fakeRole = Role.SEER;
                    }
                    else if (!fakeRoles.Contains(Role.MEDIUM))
                    {
                        fakeRole = Role.MEDIUM;
                    }
                    else
                    {
                        fakeRole = Role.VILLAGER;
                    }
                }
                if (fakeRole != oldFakeRole)
                {
                    SetupFakeRole(fakeRole);
                }
            }
            else
            {
                attackVoteCandidate = ChooseAttackVoteCandidate();
                if (attackVoteCandidate != declaredAttackVoteCandidate)
                {
                    EnqueueWhisper(AttackContent(Me, attackVoteCandidate));
                    declaredAttackVoteCandidate = attackVoteCandidate;
                }
            }
            return DequeueWhisper();
        }

        void EnqueueWhisper(Content content)
        {
            if (content.Subject == Agent.NONE)
            {
                whisperQueue.Enqueue(ReplaceSubject(content, Me));
            }
            else
            {
                whisperQueue.Enqueue(content);
            }
        }

        string DequeueWhisper()
        {
            if (whisperQueue.Count == 0)
            {
                return Content.SKIP.Text;
            }
            var content = whisperQueue.Dequeue();
            if (content.Subject == Me)
            {
                return Content.StripSubject(content.Text);
            }
            return content.Text;
        }

        double VoteEval(Agent agent) => VoteReasonMap.GetVoteCount(agent) + fakeMetaInfo.GetRoleEstimator(Role.WEREWOLF)[agent];

        void ChooseVoteCandidate0()
        {
            VoteCandidate = AliveOthers.OrderByDescending(a => VoteEval(a)).First();
            VoteReasonMap.Put(Me, VoteCandidate);
            if (VoteReasonMap.GetVoteCount(VoteCandidate) < AliveOthers.Count * 0.5)
            {
                VoteCandidate = innerPlayer.Vote();
                if (IsWolf(VoteCandidate))
                {
                    VoteCandidate = SelectMax(Role.WEREWOLF, GetHuman(AliveOthers));
                }
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
                    if (innerPlayer.IsLikeWolf(VoteCandidate))
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

    }
}
