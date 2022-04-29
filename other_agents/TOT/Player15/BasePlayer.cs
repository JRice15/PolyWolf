//
// BasePlayer.cs
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
    /// <summary>
    /// Base class for all players.
    /// </summary>
    class BasePlayer : IPlayer
    {
        MetaInfo metaInfo;

        /// <summary>
        /// Random number generator.
        /// </summary>
        protected Random Random { get; } = new Random();

        /// <summary>
        /// Constructs BasePlayer with meta information.
        /// </summary>
        /// <param name="metaInfo">The meta information.</param>
        public BasePlayer(MetaInfo metaInfo) => this.metaInfo = metaInfo;

        /// <summary>
        /// This agent.
        /// </summary>
        protected Agent Me { get; private set; } = Agent.NONE;

        /// <summary>
        /// The role of this agent.
        /// </summary>
        protected Role MyRole { get; private set; }

        /// <summary>
        /// Date.
        /// </summary>
        protected int Date { get; private set; }

        /// <summary>
        /// Turn.
        /// </summary>
        protected int Turn { get; private set; }

        /// <summary>
        /// Advances the turn.
        /// </summary>
        protected void NextTurn() => Turn++;

        /// <summary>
        /// The index of the latest talk.
        /// </summary>
        protected int LastTalkIdx { get; private set; }

        /// <summary>
        /// Whether this is re-vote.
        /// </summary>
        protected bool IsRevote { get; set; }

        /// <summary>
        /// Whether it is in power play.
        /// </summary>
        protected bool IsPP { get; set; }

        /// <summary>
        /// Current game information.
        /// </summary>
        protected IGameInfo GameInfo { get; private set; } = default!;

        /// <summary>
        /// Other agents.
        /// </summary>
        protected List<Agent> Others => GetOthers(GameInfo.AgentList);

        /// <summary>
        /// Returns the list of other agents from the list of agents.
        /// </summary>
        /// <param name="agents">The list of agents.</param>
        /// <returns>The list of other agents.</returns>
        protected List<Agent> GetOthers(IEnumerable<Agent> agents) => agents.Where(a => a != Me).Distinct().ToList();

        /// <summary>
        /// Alive other agents.
        /// </summary>
        protected List<Agent> AliveOthers => GetAlive(Others);

        HashSet<Agent> executedAgents = new HashSet<Agent>();

        /// <summary>
        /// Returns whether the agent was executed.
        /// </summary>
        /// <param name="agent">The agent.</param>
        /// <returns>true if the agent was executed.</returns>
        protected bool IsExecuted(Agent agent) => executedAgents.Contains(agent);

        HashSet<Agent> killedAgents = new HashSet<Agent>();

        /// <summary>
        /// Returns whether the agent was killed by werewolf's attack.
        /// </summary>
        /// <param name="agent">The agent.</param>
        /// <returns>true if the agent was killed.</returns>
        protected bool IsKilled(Agent agent) => killedAgents.Contains(agent);

        /// <summary>
        /// All divination reports reported until now.
        /// </summary>
        protected List<Judge> DivinationReports { get; private set; } = new List<Judge>();

        Dictionary<Agent, Judge> divinationMap = new Dictionary<Agent, Judge>();

        /// <summary>
        /// Returns the latest divination result reported by the agent.
        /// </summary>
        /// <param name="agent">The agent.</param>
        /// <returns>Judge.Empty if not found.</returns>
        protected Judge GetDivinationBy(Agent agent) => divinationMap.TryGetValue(agent, out Judge judge) ? judge : Judge.Empty;

        /// <summary>
        /// All divination results of this agent.
        /// </summary>
        protected List<Judge> MyDivinations { get; private set; } = new List<Judge>();

        /// <summary>
        /// Returns the divination result by this agent on specified date.
        /// </summary>
        /// <param name="date">The date.</param>
        /// <returns>Judge.Empty if not found.</returns>
        protected Judge GetMyDivinationOnDay(int date) => MyDivinations.Where(j => j.Day == date).DefaultIfEmpty(Judge.Empty).First();

        /// <summary>
        /// All results of medium of this agent.
        /// </summary>
        protected List<Judge> MyIdentifications { get; private set; } = new List<Judge>();

        /// <summary>
        /// All medium reports reported until now.
        /// </summary>
        protected List<Judge> IdentReports { get; private set; } = new List<Judge>();

        Dictionary<Agent, Judge> identMap = new Dictionary<Agent, Judge>();

        /// <summary>
        /// Returns the latest medium result reported by the agent.
        /// </summary>
        /// <param name="agent">The agent.</param>
        /// <returns>Judge.Empty if not found.</returns>
        protected Judge GetIdentBy(Agent agent) => identMap.TryGetValue(agent, out Judge judge) ? judge : Judge.Empty;

        Queue<Content> talkQueue = new Queue<Content>();

        /// <summary>
        /// Vote candidate.
        /// </summary>
        protected Agent VoteCandidate { get; set; } = Agent.NONE;

        /// <summary>
        /// Declared vote candidate.
        /// </summary>
        protected Agent DeclaredVoteCandidate { get; set; } = Agent.NONE;

        /// <summary>
        /// Declared estimated werewolf.
        /// </summary>
        protected Agent DeclaredWolf { get; set; } = Agent.NONE;

        Dictionary<Agent, Role> comingoutMap = new Dictionary<Agent, Role>();

        /// <summary>
        /// Returns whether the agent has done CO.
        /// </summary>
        /// <param name="agent">The agent.</param>
        /// <returns>true if the agent has done CO.</returns>
        protected bool IsCo(Agent agent) => comingoutMap.ContainsKey(agent);

        /// <summary>
        /// Returns whether the CO of the role has been done.
        /// </summary>
        /// <param name="role">The role.</param>
        /// <returns>true if the CO of the role has been done.</returns>
        protected bool IsCo(Role role) => comingoutMap.ContainsValue(role);

        /// <summary>
        /// Returns the role of the CO the agent has done.
        /// </summary>
        /// <param name="agent">The agent.</param>
        /// <returns>Role.UNC if the agent has not done CO yet.</returns>
        protected Role GetCoRoleOf(Agent agent) => comingoutMap.TryGetValue(agent, out Role role) ? role : Role.UNC;

        /// <summary>
        /// Returns the agents claiming to be the role.
        /// </summary>
        /// <param name="role">The role.</param>
        /// <returns>The list of agents claiming to be the role.</returns>
        protected List<Agent> GetProfessed(Role role) => comingoutMap.Keys.Where(a => GetCoRoleOf(a) == role).ToList();

        int talkListHead;

        /// <summary>
        /// The mapping between agent and its estimate with reason.
        /// </summary>
        protected EstimateReasonMap EstimateReasonMap { get; } = new EstimateReasonMap();

        /// <summary>
        /// The mapping between agent and its declared vote with reason.
        /// </summary>
        protected VoteReasonMap VoteReasonMap { get; } = new VoteReasonMap();

        /// <summary>
        /// The counter of vote requests.
        /// </summary>
        protected VoteRequestCounter VoteRequestCounter { get; } = new VoteRequestCounter();

        /// <summary>
        /// Returns the probability that the agent is the role.
        /// </summary>
        /// <param name="agent">The agent.</param>
        /// <param name="role">The role.</param>
        /// <returns>The probability.</returns>
        protected double GetProbOf(Agent agent, Role role) => metaInfo.GetRoleEstimator(role)[agent];

        /// <summary>
        /// Overwrites the probability that the agent is the role, with new probability.
        /// </summary>
        /// <param name="agent">The agent.</param>
        /// <param name="role">The role.</param>
        /// <param name="prob">New probability.</param>
        public void OverwriteProbOf(Agent agent, Role role, double prob) => metaInfo.GetRoleEstimator(role)[agent] = prob;

        /// <summary>
        /// The number of games this agent participated.
        /// </summary>
        protected int GameCount => metaInfo.GameCount;

        /// <summary>
        /// Returns the number of games in which this player was the role.
        /// </summary>
        /// <param name="role">The role.</param>
        /// <returns>The number of games.</returns>
        protected int GetRoleCount(Role role) => metaInfo.GetRoleCount(role);

        /// <summary>
        /// Returns the number of win games of the agent.
        /// </summary>
        /// <param name="agent">The agent</param>
        /// <returns>The number of win games.</returns>
        protected int GetWinCount(Agent agent) => metaInfo.GetWinCount(agent);

        /// <summary>
        /// Returns whether the agent can do PP.
        /// </summary>
        /// <param name="agent">The agent</param>
        /// <returns>true if the agent can do PP.</returns>
        protected bool GetPpAbility(Agent agent) => metaInfo.GetPpAbility(agent);

        /// <summary>
        /// Returns whether the agent is like a seer.
        /// </summary>
        /// <param name="agent">The agent.</param>
        /// <returns>true if the agent is like a seer.</returns>
        public bool IsLikeSeer(Agent agent) => MaxRole(agent) == Role.SEER;

        /// <summary>
        /// Returns whether the agent is like a werewolf.
        /// </summary>
        /// <param name="agent">The agent.</param>
        /// <returns>true if the agent is like a werewolf.</returns>
        public bool IsLikeWolf(Agent agent) => IsGray(agent) && MaxRole(agent) == Role.WEREWOLF;

        /// <summary>
        /// Returns the agent's role with the highest probability.
        /// </summary>
        /// <param name="agent">The agent.</param>
        /// <returns>Role.UNC if not found.</returns>
        protected Role MaxRole(Agent agent) => GameInfo.ExistingRoleList.OrderByDescending(r => GetProbOf(agent, r)).DefaultIfEmpty(Role.UNC).First();

        /// <summary>
        /// Returns the agent with the highest role probability from candidates.
        /// </summary>
        /// <param name="role">The role.</param>
        /// <param name="agents">The candidates.</param>
        /// <param name="excludes">The agents to be excluded.</param>
        /// <returns>Agent.NONE if not found.</returns>
        protected Agent SelectMax(Role role, IEnumerable<Agent> agents, params Agent[] excludes) => metaInfo.GetRoleEstimator(role).Max(agents, excludes);

        /// <summary>
        /// Returns the agent with the lowest role probability from candidates.
        /// </summary>
        /// <param name="role">The role.</param>
        /// <param name="agents">The candidates.</param>
        /// <param name="excludes">The agents to be excluded.</param>
        /// <returns>Agent.NONE if not found.</returns>
        protected Agent SelectMin(Role role, IEnumerable<Agent> agents, params Agent[] excludes) => metaInfo.GetRoleEstimator(role).Min(agents, excludes);

        /// <summary>
        /// Returns the list of agents sorted by role probability in ascending order.
        /// </summary>
        /// <param name="role">The role.</param>
        /// <param name="agents">The list of agents to be sorted.</param>
        /// <returns>The sorted list of agents.</returns>
        protected List<Agent> Ascending(Role role, IEnumerable<Agent> agents) => metaInfo.GetRoleEstimator(role).Ascneding(agents);

        /// <summary>
        /// Returns the list of agents sorted by role probability in descending order.
        /// </summary>
        /// <param name="role">The role.</param>
        /// <param name="agents">The list of agents to be sorted.</param>
        /// <returns>The sorted list of agents.</returns>
        protected List<Agent> Descending(Role role, IEnumerable<Agent> agents) => metaInfo.GetRoleEstimator(role).Descneding(agents);

        Dictionary<Agent, Species> speciesMap = new Dictionary<Agent, Species>();

        /// <summary>
        /// Returns whether the agent is human.
        /// </summary>
        /// <param name="agent">The agent.</param>
        /// <returns>true if the agent is human.</returns>
        protected bool IsHuman(Agent agent) => speciesMap.TryGetValue(agent, out Species species) && species == Species.HUMAN;

        /// <summary>
        /// Sets the agent to be human.
        /// </summary>
        /// <param name="agent">The agent.</param>
        protected void SetHuman(Agent agent) => speciesMap[agent] = Species.HUMAN;

        /// <summary>
        /// Returns the list of human agents from the candidates.
        /// </summary>
        /// <param name="agents">The candidates.</param>
        /// <returns>The list of human agents.</returns>
        protected List<Agent> GetHuman(IEnumerable<Agent> agents) => agents.Where(a => IsHuman(a)).ToList();

        /// <summary>
        /// Returns whether the agent is unjudged.
        /// </summary>
        /// <param name="agent">The agent.</param>
        /// <returns>true if the agent is unjudged.</returns>
        protected bool IsGray(Agent agent) => speciesMap.TryGetValue(agent, out Species species) && species != Species.HUMAN && species != Species.WEREWOLF;

        /// <summary>
        /// Sets the agent to be unjudged.
        /// </summary>
        /// <param name="agent">The agent</param>
        protected void SetGray(Agent agent) => speciesMap[agent] = Species.UNC;

        /// <summary>
        /// Returns the list of unjudged agents from the candidates.
        /// </summary>
        /// <param name="agents">The candidates.</param>
        /// <returns>The list of unjudged agents.</returns>
        protected List<Agent> GetGray(IEnumerable<Agent> agents) => agents.Where(a => IsGray(a)).ToList();

        /// <summary>
        /// Returns whether the agent is werewolf.
        /// </summary>
        /// <param name="agent">The agent.</param>
        /// <returns>true if the agent is werewolf.</returns>
        protected bool IsWolf(Agent agent) => speciesMap.TryGetValue(agent, out Species species) && species == Species.WEREWOLF;

        /// <summary>
        /// Sets the agent to be werewolf.
        /// </summary>
        /// <param name="agent">The agent.</param>
        protected void SetWolf(Agent agent) => speciesMap[agent] = Species.WEREWOLF;

        /// <summary>
        /// Returns the list of werewolves from the candidates.
        /// </summary>
        /// <param name="agents">The candidates.</param>
        /// <returns>the list of werewolf agents.</returns>
        public List<Agent> GetWolf(IEnumerable<Agent> agents) => agents.Where(a => IsWolf(a)).ToList();

        /// <summary>
        /// Whethre this agent has found a werewolf.
        /// </summary>
        protected bool FoundWolf => speciesMap.ContainsValue(Species.WEREWOLF);

        /// <summary>
        /// Fake seers.
        /// </summary>
        protected List<Agent> FakeSeers
        {
            get
            {
                if (MyRole == Role.SEER)
                {
                    return GetProfessed(Role.SEER);
                }
                else
                {
                    return DivinationReports.Where(j => Conflicts(j)).Select(j => j.Agent).Distinct().ToList();
                }
            }
        }

        /// <summary>
        /// Return whether the agent is a fake seer.
        /// </summary>
        /// <param name="agent">The agent.</param>
        /// <returns>true if the agent is a fake seer.</returns>
        protected bool IsFakeSeer(Agent agent) => FakeSeers.Contains(agent);

        /// <summary>
        /// Fake mediums.
        /// </summary>
        protected List<Agent> FakeMediums
        {
            get
            {
                if (MyRole == Role.MEDIUM)
                {
                    return GetProfessed(Role.MEDIUM);
                }
                else
                {
                    return IdentReports.Where(j => Conflicts(j)).Select(j => j.Agent).Distinct().ToList();
                }
            }
        }

        /// <summary>
        /// Return whether the agent is a fake medium.
        /// </summary>
        /// <param name="agent">The agent.</param>
        /// <returns>true if the agent is a fake medium.</returns>
        protected bool IsFakeMedium(Agent agent) => FakeMediums.Contains(agent);

        /// <summary>
        /// Returns whether the judge conflicts known judges.
        /// </summary>
        /// <param name="j">The judge.</param>
        /// <returns>true if the judge conflicts known judges.</returns>
        protected bool Conflicts(Judge j) => (IsHuman(j.Target) && j.Result == Species.WEREWOLF) || (IsWolf(j.Target) && j.Result == Species.HUMAN);

        /// <summary>
        /// Returns the agents estimated to be the role by this agent.
        /// </summary>
        /// <param name="role">The role.</param>
        /// <returns>The list of agents estimated to be the role.</returns>
        protected List<Agent> GetEstimates(Role role) => EstimateReasonMap.GetEstimated(Me, role);

        /// <summary>
        /// Sets the estimated target's role by this agent.
        /// </summary>
        /// <param name="target">the target.</param>
        /// <param name="role">The estimated role.</param>
        /// <remarks>If Role.UNC is given, the estimate about the target is removed.</remarks>
        protected void SetEstimate(Agent target, Role role)
        {
            if (role != Role.UNC)
            {
                EstimateReasonMap.Put(new Estimate(Me, target, role));
            }
            else
            {
                if (EstimateReasonMap.ContainsKey(Me))
                {
                    EstimateReasonMap[Me].Remove(target);
                }
            }
        }

        /// <summary>
        /// Returns whether this player estimates the agent as the role.
        /// </summary>
        /// <param name="agent">The agent</param>
        /// <param name="role">The role</param>
        /// <returns>true if this player estimates the agent as the role.</returns>
        protected bool IsEstimated(Agent agent, Role role)
        {
            if (EstimateReasonMap.TryGetValue(Me, out var map) && map.TryGetValue(agent, out var estimate))
            {
                return estimate.HasRole(role);

            }
            return false;
        }

        /// <summary>
        /// Returns whether the agent is alive.
        /// </summary>
        /// <param name="agent">The agent.</param>
        /// <returns>true if the agent is alive.</returns>
        protected bool IsAlive(Agent agent) => GameInfo.StatusMap.TryGetValue(agent, out Status status) && status == Status.ALIVE;

        /// <summary>
        /// Returns whether the agent is dead.
        /// </summary>
        /// <param name="agent">The agent.</param>
        /// <returns>true if the agent is dead.</returns>
        protected bool IsDead(Agent agent) => GameInfo.StatusMap.TryGetValue(agent, out Status status) && status == Status.DEAD;

        /// <summary>
        /// Returns the list of alive agents from the given agents.
        /// </summary>
        /// <param name="agents">The given agents.</param>
        /// <returns>The list of alive agents.</returns>
        protected List<Agent> GetAlive(IEnumerable<Agent> agents) => agents.Where(a => IsAlive(a)).Distinct().ToList();

        /// <summary>
        /// Returns the list of dead agents from the given agents.
        /// </summary>
        /// <param name="agents">The given agents.</param>
        /// <returns>The list of dead agents.</returns>
        protected List<Agent> GetDead(IEnumerable<Agent> agents) => agents.Where(a => IsDead(a)).Distinct().ToList();

        /// <summary>
        /// Returns an agent randomly chosen from the list of agents.
        /// </summary>
        /// <param name="agentList">The list of agents.</param>
        /// <returns>Agent.NONE if the agent list is empty.</returns>
        protected Agent RandomSelect(IEnumerable<Agent> agentList) => agentList.DefaultIfEmpty(Agent.NONE).Shuffle().First();

        /// <summary>
        /// Whether if the role exists in this village.
        /// </summary>
        /// <param name="role">The role.</param>
        /// <returns>true if the role exists.</returns>
        protected bool Exists(Role role) => GameInfo.ExistingRoleList.Contains(role);

        /// <summary>
        /// The name of this agent.
        /// </summary>
        public string Name => System.Reflection.Assembly.GetExecutingAssembly().GetName().Name;

        /// <summary>
        /// Initiallizes a new game.
        /// </summary>
        /// <param name="gameInfo">The GameInfo.</param>
        /// <param name="gameSetting">The GameSetting.</param>
        public virtual void Initialize(IGameInfo gameInfo, IGameSetting gameSetting)
        {
            GameInfo = gameInfo;
            Date = -1;
            IsPP = false;
            Me = gameInfo.Agent;
            MyRole = gameInfo.Role;
            executedAgents.Clear();
            killedAgents.Clear();
            DivinationReports.Clear();
            divinationMap.Clear();
            IdentReports.Clear();
            identMap.Clear();
            MyDivinations.Clear();
            MyIdentifications.Clear();
            comingoutMap.Clear();
            EstimateReasonMap.Clear();
            speciesMap.Clear();
            if (MyRole != Role.WEREWOLF)
            {
                gameInfo.AgentList.ToList().ForEach(a => speciesMap[a] = Species.UNC);
                speciesMap[Me] = Species.HUMAN;
            }
            else
            {
                gameInfo.AgentList.ToList().ForEach(a => speciesMap[a] = Species.HUMAN);
                gameInfo.RoleMap.Keys.ToList().ForEach(a => speciesMap[a] = Species.WEREWOLF);
            }
        }

        /// <summary>
        /// Updates this agent's status using the GameInfo.
        /// </summary>
        /// <param name="gameInfo">The GameInfo.</param>
        public virtual void Update(IGameInfo gameInfo)
        {
            GameInfo = gameInfo;
            if (gameInfo.Day == Date + 1)
            {
                Date = gameInfo.Day;
                return;
            }

#nullable disable
            if (gameInfo.LatestExecutedAgent != null)
            {
                AddExecutedAgent(gameInfo.LatestExecutedAgent);
            }
#nullable restore

            for (var i = talkListHead; i < gameInfo.TalkList.Count; i++)
            {
                var talk = gameInfo.TalkList[i];
                LastTalkIdx = talk.Idx;
                var talker = talk.Agent;
                if (talker == Me)
                {
                    continue;
                }
                var content = new Content(talk.Text);
                if (content.Subject == Agent.NONE)
                {
                    content = ReplaceSubject(content, talker);
                }
                ParseSentence(content);
            }

            if (gameInfo.AgentList.Count == 5)
            {
                GetDead(Others).ForEach(a => SetHuman(a));
            }

            talkListHead = gameInfo.TalkList.Count;
        }

        /// <summary>
        /// Parses the sentence.
        /// </summary>
        /// <param name="sentence">The sentence.</param>
        protected void ParseSentence(Content sentence)
        {
            if (EstimateReasonMap.Put(sentence) || VoteReasonMap.Put(sentence))
            {
                return;
            }

            switch (sentence.Topic)
            {
                case Topic.COMINGOUT:
                    comingoutMap[sentence.Target] = sentence.Role;
                    if (sentence.Role == Role.WEREWOLF || sentence.Role == Role.POSSESSED)
                    {
                        metaInfo.SetPpAbility(sentence.Target, true);
                    }
                    return;
                case Topic.DIVINED:
                    DivinationReports.Add(new Judge(Date, sentence.Subject, sentence.Target, sentence.Result));
                    divinationMap[sentence.Subject] = DivinationReports.Last();
                    return;
                case Topic.IDENTIFIED:
                    IdentReports.Add(new Judge(Date, sentence.Subject, sentence.Target, sentence.Result));
                    identMap[sentence.Subject] = IdentReports.Last();
                    return;
                case Topic.OPERATOR:
                    ParseOperator(sentence);
                    return;
                default:
                    break;
            }
        }

        /// <summary>
        /// Parses the operator sentence.
        /// </summary>
        /// <param name="sentence">The operator sentence.</param>
        protected void ParseOperator(Content sentence)
        {
            switch (sentence.Operator)
            {
                case Operator.BECAUSE:
                    ParseSentence(sentence.ContentList[1]);
                    break;
                case Operator.DAY:
                    ParseSentence(sentence.ContentList[0]);
                    break;
                case Operator.AND:
                case Operator.OR:
                case Operator.XOR:
                    sentence.ContentList.ToList().ForEach(c => ParseSentence(c));
                    break;
                case Operator.REQUEST:
                    if (VoteRequestCounter.Add(sentence))
                    {
                        return;
                    }
                    break;
                case Operator.INQUIRE:
                    break;
                default:
                    break;
            }
        }

        /// <summary>
        /// Initializes this agent's status at the beginning of the day. 
        /// </summary>
        public virtual void DayStart()
        {
            foreach (var a in GameInfo.LastDeadAgentList)
            {
                AddKilledAgent(a);
            }

#nullable disable
            if (GameInfo.ExecutedAgent != null)
            {
                AddExecutedAgent(GameInfo.ExecutedAgent);
            }

            var divination = GameInfo.DivineResult;
            if (divination != null)
            {
                MyDivinations.Add(divination);
                if (divination.Result == Species.WEREWOLF)
                {
                    SetWolf(divination.Target);
                }
                else
                {
                    SetHuman(divination.Target);
                }
            }
            var ident = GameInfo.MediumResult;
            if (ident != null)
            {
                MyIdentifications.Add(ident);
                if (ident.Result == Species.WEREWOLF)
                {
                    SetWolf(ident.Target);
                }
                else
                {
                    SetHuman(ident.Target);
                }
            }
#nullable restore

            IsRevote = false;
            talkQueue.Clear();
            DeclaredVoteCandidate = Agent.NONE;
            DeclaredWolf = Agent.NONE;
            VoteCandidate = Agent.NONE;
            talkListHead = 0;
            VoteReasonMap.Clear();
            VoteRequestCounter.Clear();
            Turn = 0;
            LastTalkIdx = -1;
        }

        void AddExecutedAgent(Agent executedAgent) => executedAgents.Add(executedAgent);

        void AddKilledAgent(Agent killedAgent)
        {
            killedAgents.Add(killedAgent);
            SetHuman(killedAgent);
        }

        /// <summary>
        /// Chooses the candidate for voting.
        /// </summary>
        /// <param name="isLast">Whether this call is just before voting.</param>
        protected virtual void ChooseVoteCandidate(bool isLast)
        {
            if (isLast)
            {
                VoteCandidate = AdjustVote(VoteReasonMap, Me, 0.5);
            }
        }

        /// <summary>
        /// Returns string of this agent's talk..
        /// </summary>
        /// <returns>The string of talk.</returns>
        public virtual string Talk()
        {
            ChooseVoteCandidate(isLast: false);
            if (VoteCandidate != DeclaredVoteCandidate)
            {
                CancelVoting();
                CancelVoteRequest(Agent.ANY);
                if (VoteCandidate.IsValid())
                {
                    EnqueueTalk(VoteContent(Me, VoteCandidate));
                    EnqueueTalk(RequestContent(Me, Agent.ANY, VoteContent(Agent.ANY, VoteCandidate)));
                }
                DeclaredVoteCandidate = VoteCandidate;
            }
            NextTurn();
            return DequeueTalk();
        }

        /// <summary>
        /// Enqueues content to the talk queue.
        /// </summary>
        /// <param name="content">The content.</param>
        protected void EnqueueTalk(Content content)
        {
            if (content.Subject == Agent.NONE)
            {
                talkQueue.Enqueue(ReplaceSubject(content, Me));
            }
            else
            {
                talkQueue.Enqueue(content);
            }
        }

        /// <summary>
        /// Dequeues the talk queue.
        /// </summary>
        /// <returns>The content at the head of the talk queue.</returns>
        protected string DequeueTalk()
        {
            if (talkQueue.Count == 0)
            {
                return Content.SKIP.Text;
            }
            var content = talkQueue.Dequeue();
            if (content.Subject == Me)
            {
                return Content.StripSubject(content.Text);
            }
            return content.Text;
        }

        /// <summary>
        /// Returns the target of ellimination vote.
        /// </summary>
        /// <returns>The target agent.</returns>
        public virtual Agent Vote()
        {
            ChooseVoteCandidate(isLast: true);
            IsRevote = true;
            return VoteCandidate;
        }

        /// <summary>
        /// Adjusts vote candidate considering the vote declarations.
        /// </summary>
        /// <param name="vrmap">The VoteReasonMap.</param>
        /// <param name="agent">The agent to be excluded.</param>
        /// <param name="threshold">The threshold of the ratio of vote count to the total vote count.</param>
        /// <returns>The adjusted vote candidate.</returns>
        protected Agent AdjustVote(VoteReasonMap vrmap, Agent agent, double threshold)
        {
            var voted = vrmap.GetTarget(Me);

            if (vrmap.VoteCount < AliveOthers.Count * threshold)
            {
                return voted;
            }

            vrmap.Remove(Me);
            var winners = vrmap.Winners;
            var orderedList = vrmap.GetOrderedList(agent, Me);
            vrmap.Put(Me, voted);

            if (winners.Contains(voted) && winners.Contains(agent))
            {
                if (orderedList.Count > 0)
                {
                    return orderedList[0];
                }
            }
            return voted;
        }

        /// <summary>
        /// Returns the string of this agent's whisper.
        /// </summary>
        /// <returns>The target agent.</returns>
        public virtual string Whisper() => Content.SKIP.Text;

        /// <summary>
        /// Returns the target of this agent's attack.
        /// </summary>
        /// <returns>The target agent.</returns>
        public virtual Agent Attack() => Agent.NONE;

        /// <summary>
        /// Returns the target of this agent's divination.
        /// </summary>
        /// <returns>The target agent.</returns>
        public virtual Agent Divine() => Agent.NONE;

        /// <summary>
        /// Returns the target of this agent's guard.
        /// </summary>
        /// <returns>The target agent.</returns>
        public virtual Agent Guard() => Agent.NONE;

        /// <summary>
        /// Processing at the end of the game.
        /// </summary>
        public virtual void Finish() { }

        /// <summary>
        /// Replaces the subject of content with a new subject.
        /// </summary>
        /// <param name="content">The content.</param>
        /// <param name="newSubject">New subject.</param>
        /// <returns>The modified content.</returns>
        protected static Content ReplaceSubject(Content content, Agent newSubject)
        {
            if (content.Topic == Topic.Skip || content.Topic == Topic.Over)
            {
                return content;
            }
            if (newSubject == Agent.NONE)
            {
                return new Content(Content.StripSubject(content.Text));
            }
            else
            {
                return new Content(newSubject + " " + Content.StripSubject(content.Text));
            }
        }

        /// <summary>
        /// The sintax sugar of the conten of agreement.
        /// </summary>
        /// <param name="subject"></param>
        /// <param name="talkType"></param>
        /// <param name="talkDay"></param>
        /// <param name="talkID"></param>
        /// <returns></returns>
        protected static Content AgreeContent(Agent subject, UtteranceType talkType, int talkDay, int talkID)
            => new Content(new AgreeContentBuilder(subject, talkType, talkDay, talkID));

        /// <summary>
        /// The sintax sugar of the content of disagreement.
        /// </summary>
        /// <param name="subject"></param>
        /// <param name="talkType"></param>
        /// <param name="talkDay"></param>
        /// <param name="talkID"></param>
        /// <returns></returns>
        protected static Content DisagreeContent(Agent subject, UtteranceType talkType, int talkDay, int talkID)
            => new Content(new DisagreeContentBuilder(subject, talkType, talkDay, talkID));

        /// <summary>
        /// The sintax sugar of the content of voting will.
        /// </summary>
        /// <param name="subject"></param>
        /// <param name="target"></param>
        /// <returns></returns>
        protected static Content VoteContent(Agent subject, Agent target)
            => new Content(new VoteContentBuilder(subject, target ?? Agent.ANY));

        /// <summary>
        /// The sintax sugar of the content of the vote report.
        /// </summary>
        /// <param name="subject"></param>
        /// <param name="target"></param>
        /// <returns></returns>
        protected static Content VotedContent(Agent subject, Agent target)
            => new Content(new VotedContentBuilder(subject, target ?? Agent.ANY));

        /// <summary>
        /// The sintax sugar of the content of attack voting will.
        /// </summary>
        /// <param name="subject"></param>
        /// <param name="target"></param>
        /// <returns></returns>
        protected static Content AttackContent(Agent subject, Agent target)
            => new Content(new AttackContentBuilder(subject, target ?? Agent.ANY));

        /// <summary>
        /// The sintax sugar of the content of the attack vote report.
        /// </summary>
        /// <param name="subject"></param>
        /// <param name="target"></param>
        /// <returns></returns>
        protected static Content AttackedContent(Agent subject, Agent target)
            => new Content(new AttackedContentBuilder(subject, target ?? Agent.ANY));

        /// <summary>
        /// The sintax sugar of the content of guard will.
        /// </summary>
        /// <param name="subject"></param>
        /// <param name="target"></param>
        /// <returns></returns>
        protected static Content GuardContent(Agent subject, Agent target)
            => new Content(new GuardContentBuilder(subject, target ?? Agent.ANY));

        /// <summary>
        /// The sintax sugar of the content of the guard report.
        /// </summary>
        /// <param name="subject"></param>
        /// <param name="target"></param>
        /// <returns></returns>
        protected static Content GuardedContent(Agent subject, Agent target)
            => new Content(new GuardedAgentContentBuilder(subject, target ?? Agent.ANY));

        /// <summary>
        /// The sintax sugar of the content of estimate.
        /// </summary>
        /// <param name="subject"></param>
        /// <param name="target"></param>
        /// <param name="role"></param>
        /// <returns></returns>
        protected static Content EstimateContent(Agent subject, Agent target, Role role)
            => new Content(new EstimateContentBuilder(subject, target ?? Agent.ANY, role));

        /// <summary>
        /// The sintax sugar of the content of CO.
        /// </summary>
        /// <param name="subject"></param>
        /// <param name="target"></param>
        /// <param name="role"></param>
        /// <returns></returns>
        protected static Content CoContent(Agent subject, Agent target, Role role)
            => new Content(new ComingoutContentBuilder(subject, target ?? Agent.ANY, role));

        /// <summary>
        /// The sintax sugar of the content of request.
        /// </summary>
        /// <param name="subject"></param>
        /// <param name="target"></param>
        /// <param name="content"></param>
        /// <returns></returns>
        protected static Content RequestContent(Agent subject, Agent target, Content content)
            => new Content(new RequestContentBuilder(subject, target ?? Agent.ANY, content));

        /// <summary>
        /// The sintax sugar of the content of inquiry.
        /// </summary>
        /// <param name="subject"></param>
        /// <param name="target"></param>
        /// <param name="content"></param>
        /// <returns></returns>
        protected static Content InquiryContent(Agent subject, Agent target, Content content)
            => new Content(new InquiryContentBuilder(subject, target ?? Agent.ANY, content));

        /// <summary>
        /// The sintax sugar of the content of divination.
        /// </summary>
        /// <param name="subject"></param>
        /// <param name="target"></param>
        /// <returns></returns>
        protected static Content DivinationContent(Agent subject, Agent target)
            => new Content(new DivinationContentBuilder(subject, target ?? Agent.ANY));

        /// <summary>
        /// The sintax sugar of the content of divination report.
        /// </summary>
        /// <param name="subject"></param>
        /// <param name="target"></param>
        /// <param name="result"></param>
        /// <returns></returns>
        protected static Content DivinedContent(Agent subject, Agent target, Species result)
            => new Content(new DivinedResultContentBuilder(subject, target ?? Agent.ANY, result));

        /// <summary>
        /// The sintax sugar of the content of identification report.
        /// </summary>
        /// <param name="subject"></param>
        /// <param name="target"></param>
        /// <param name="result"></param>
        /// <returns></returns>
        protected static Content IdentContent(Agent subject, Agent target, Species result)
            => new Content(new IdentContentBuilder(subject, target ?? Agent.ANY, result));

        /// <summary>
        /// The sintax sugar of the AND content.
        /// </summary>
        /// <param name="subject"></param>
        /// <param name="contents"></param>
        /// <returns></returns>
        protected static Content AndContent(Agent subject, params Content[] contents)
            => new Content(new AndContentBuilder(subject, contents));

        /// <summary>
        /// The sintax sugar of the OR content.
        /// </summary>
        /// <param name="subject"></param>
        /// <param name="contents"></param>
        /// <returns></returns>
        protected static Content OrContent(Agent subject, params Content[] contents)
            => new Content(new OrContentBuilder(subject, contents));

        /// <summary>
        /// The sintax sugar of the XOR content.
        /// </summary>
        /// <param name="subject"></param>
        /// <param name="content1"></param>
        /// <param name="content2"></param>
        /// <returns></returns>
        protected static Content XorContent(Agent subject, Content content1, Content content2)
            => new Content(new XorContentBuilder(subject, content1, content2));

        /// <summary>
        /// The sintax sugar of the NOT content.
        /// </summary>
        /// <param name="subject"></param>
        /// <param name="content"></param>
        /// <returns></returns>
        protected static Content NotContent(Agent subject, Content content)
            => new Content(new NotContentBuilder(subject, content));

        /// <summary>
        /// The sintax sugar of the DAY content.
        /// </summary>
        /// <param name="subject"></param>
        /// <param name="day"></param>
        /// <param name="content"></param>
        /// <returns></returns>
        protected static Content DayContent(Agent subject, int day, Content content)
            => new Content(new DayContentBuilder(subject, day, content));

        /// <summary>
        /// The sintax sugar of the BECAUSE content.
        /// </summary>
        /// <param name="subject"></param>
        /// <param name="reason"></param>
        /// <param name="action"></param>
        /// <returns></returns>
        protected static Content BecauseContent(Agent subject, Content reason, Content action)
            => new Content(new BecauseContentBuilder(subject, reason, action));

        /// <summary>
        /// Removes the content from the talk queue.
        /// </summary>
        /// <param name="content">The content.</param>
        protected void CancelTalk(Content content)
        {
            talkQueue = new Queue<Content>(talkQueue.Where(c =>
            {
                if (c.Equals(content))
                {
                    return false;
                }
                else if (c.Topic == content.Topic)
                {
                    if (c.Topic == Topic.VOTE)
                    {
                        return false;
                    }
                    else if (c.Topic == Topic.COMINGOUT || c.Topic == Topic.ESTIMATE || c.Topic == Topic.DIVINED || c.Topic == Topic.IDENTIFIED)
                    {
                        if (c.Target == content.Target)
                        {
                            return false;
                        }
                    }
                    else if (c.Topic == Topic.OPERATOR && c.Operator == Operator.REQUEST)
                    {
                        var req = c.ContentList.First();
                        if (req.Topic == Topic.VOTE && req.Subject == c.Target)
                        {
                            return false;
                        }
                    }
                }
                return true;
            }));
        }

        /// <summary>
        /// Removes all contents from the talk queue.
        /// </summary>
        protected void CancelAllTalk() => talkQueue.Clear();

        /// <summary>
        /// Utters a CO talk.
        /// </summary>
        /// <param name="role">The role.</param>
        protected void TalkCo(Role role)
        {
            CancelCo();
            EnqueueTalk(CoContent(Me, Me, role));
        }

        /// <summary>
        /// Removes CO content from the talk queue.
        /// </summary>
        protected void CancelCo()
        {
            CancelTalk(CoContent(Me, Me, Role.ANY));
        }

        /// <summary>
        /// Utters an estimate content.
        /// </summary>
        /// <param name="target">The target.</param>
        /// <param name="role">The role.</param>
        protected void TalkEstimate(Agent target, Role role)
        {
            CancelEstimate(target);
            EnqueueTalk(EstimateContent(Me, target, role));
        }

        /// <summary>
        /// Removes estimate content from the talk queue.
        /// </summary>
        /// <param name="target">The target.</param>
        protected void CancelEstimate(Agent target)
        {
            CancelTalk(EstimateContent(Me, target, Role.ANY));
        }

        /// <summary>
        /// Utters a vote content.
        /// </summary>
        /// <param name="target">The target.</param>
        protected void TalkVoting(Agent target)
        {
            CancelVoting();
            EnqueueTalk(VoteContent(Me, target));
        }

        /// <summary>
        /// Removes vote content from the talk queue.
        /// </summary>
        protected void CancelVoting()
        {
            CancelTalk(VoteContent(Me, Agent.ANY));
        }

        /// <summary>
        /// Utters a divination report.
        /// </summary>
        /// <param name="target">The target.</param>
        /// <param name="result">The result of the divination.</param>
        protected void TalkDivined(Agent target, Species result)
        {
            CancelDivined(target);
            EnqueueTalk(DivinedContent(Me, target, result));
        }

        /// <summary>
        /// Removes divination report from the talk queue.
        /// </summary>
        /// <param name="target">The target.</param>
        protected void CancelDivined(Agent target)
        {
            CancelTalk(DivinedContent(Me, target, Species.ANY));
        }

        /// <summary>
        /// Utters an identification report.
        /// </summary>
        /// <param name="target">The target.</param>
        /// <param name="result">The result of the identification.</param>
        protected void TalkIdentified(Agent target, Species result)
        {
            CancelIdentified(target);
            EnqueueTalk(IdentContent(Me, target, result));
        }

        /// <summary>
        /// Removes identification report from the talk queue.
        /// </summary>
        /// <param name="target">The target.</param>
        protected void CancelIdentified(Agent target)
        {
            CancelTalk(IdentContent(Me, target, Species.ANY));
        }

        /// <summary>
        /// Utters an vote request.
        /// </summary>
        /// <param name="destination">The request destination.</param>
        /// <param name="target">The vote target.</param>
        protected void TalkVoteRequest(Agent destination, Agent target)
        {
            CancelVoteRequest(destination);
            EnqueueTalk(RequestContent(Me, destination, VoteContent(destination, target)));
        }

        /// <summary>
        /// Removes vote request from the talk queue.
        /// </summary>
        /// <param name="destination">The request destination.</param>
        protected void CancelVoteRequest(Agent destination)
        {
            CancelTalk(RequestContent(Me, destination, VoteContent(destination, Agent.ANY)));
        }

    }

    static class TOTExtensions
    {
        public static bool IsValid(this Agent? agent) => agent != null && agent != Agent.NONE;
    }
}
