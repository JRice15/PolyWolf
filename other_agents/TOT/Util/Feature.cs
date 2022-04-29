//
// Feature.cs
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
    /// 
    /// </summary>
    class Feature
    {
        // role-related constants
        public static readonly int NumRoles = 6;
        public static readonly Dictionary<Role, int> RoleIntMap = new Dictionary<Role, int>
        {
            [Role.WEREWOLF] = 0,
            [Role.VILLAGER] = 1,
            [Role.SEER] = 2,
            [Role.POSSESSED] = 3,
            [Role.MEDIUM] = 4,
            [Role.BODYGUARD] = 5
        };
        public static readonly Dictionary<Role, double[]> RoleVectorMap = new Dictionary<Role, double[]>
        {

            [Role.UNC] = new double[] { 0, 0, 0, 0, 0, 0 },
            [Role.WEREWOLF] = new double[] { 1, 0, 0, 0, 0, 0 },
            [Role.VILLAGER] = new double[] { 0, 1, 0, 0, 0, 0 },
            [Role.SEER] = new double[] { 0, 0, 1, 0, 0, 0 },
            [Role.POSSESSED] = new double[] { 0, 0, 0, 1, 0, 0 },
            [Role.MEDIUM] = new double[] { 0, 0, 0, 0, 1, 0 },
            [Role.BODYGUARD] = new double[] { 0, 0, 0, 0, 0, 1 }
        };

        // constants related to the features of each agent
        public static readonly int NumAgentFeature = 18;
        // [0] 1 if dead
        public static readonly int IsDead = 0;
        // [1] the number of human judges received
        public static readonly int NumJudgedAsWhite = 1;
        // [2] the number of werewolf judges received
        public static readonly int NumJudgedAsBlack = 2;
        // [3] 1 if CO werewolf
        public static readonly int CoWerewolf = 3;
        // [4] 1 if CO villager
        public static readonly int CoVillager = 4;
        // [5] 1 if CO seer
        public static readonly int CoSeer = 5;
        // [6] 1 if CO possessed human
        public static readonly int CoPossessed = 6;
        // [7] 1 if CO medium
        public static readonly int CoMedium = 7;
        // [8] 1 if CO bodyguard
        public static readonly int CoBodyguard = 8;
        // [9] the number of human judges reported
        public static readonly int NumWhiteJudgement = 9;
        // [10] the number of werewolf judges reported
        public static readonly int NumBlackJudgement = 10;
        // [11] the number of votes different from voting declaration
        public static readonly int NumChangeVote = 11;
        // [12] 1 if enemy
        public static readonly int IsEnemy = 12;
        // [13] 1 if ally
        public static readonly int IsAlly = 13;
        // [14] 1 if human
        public static readonly int IsHuman = 14;
        // [15] 1 if werewolf
        public static readonly int IsWerewolf = 15;
        // [16] 1 if executed
        public static readonly int IsExecuted = 16;
        // [17] 1 if killed
        public static readonly int IsKilled = 17;

        // utterance-related constants
        public static readonly int NumTopics = 7;
        public static readonly int NumTurns = 10;
        public static readonly int UtSkip = 0;
        public static readonly int UtVote = 1;
        public static readonly int UtEstimate = 2;
        public static readonly int UtCo = 3;
        public static readonly int UtDivined = 4;
        public static readonly int UtIdentified = 5;
        public static readonly int UtOperator = 6;

        public static readonly Dictionary<Topic, int> TopicIntMap = new Dictionary<Topic, int>
        {
            [Topic.Skip] = UtSkip,
            [Topic.Over] = UtSkip,
            [Topic.VOTE] = UtVote,
            [Topic.ESTIMATE] = UtEstimate,
            [Topic.COMINGOUT] = UtCo,
            [Topic.DIVINED] = UtDivined,
            [Topic.IDENTIFIED] = UtIdentified,
            [Topic.OPERATOR] = UtOperator
        };

        Dictionary<Agent, AgentFeature> featureMap = new Dictionary<Agent, AgentFeature>();

        Agent me;
        Role myRole;
        int date = -1;
        int talkListHead;

        public bool IsModified { get; private set; }

        // divine result
        Dictionary<Agent, Dictionary<Agent, Species>> divinationMap = new Dictionary<Agent, Dictionary<Agent, Species>>();
        // medium result
        Dictionary<Agent, Dictionary<Agent, Species>> identMap = new Dictionary<Agent, Dictionary<Agent, Species>>();
        // confirmed information
        Dictionary<Agent, Species> speciesMap = new Dictionary<Agent, Species>();
        // voting declaration
        Dictionary<Agent, Vote> votingMap = new Dictionary<Agent, Vote>();
        // CO
        Dictionary<Agent, Role> comingoutMap = new Dictionary<Agent, Role>();
        // estimate
        Dictionary<Agent, Dictionary<Agent, Role>> estimateMap = new Dictionary<Agent, Dictionary<Agent, Role>>();
        // utterance statistics
        Dictionary<Agent, UtteranceStatistics> statMap = new Dictionary<Agent, UtteranceStatistics>();

        /// <summary>
        /// Constructs Feature with a GameInfo.
        /// </summary>
        /// <param name="gameInfo">the GameInfo</param>
        public Feature(IGameInfo gameInfo)
        {
            me = gameInfo.Agent;
            myRole = gameInfo.Role;
            foreach (var a in gameInfo.AgentList)
            {
                featureMap[a] = new AgentFeature(new double[NumAgentFeature]);
                divinationMap[a] = new Dictionary<Agent, Species>();
                identMap[a] = new Dictionary<Agent, Species>();
                estimateMap[a] = new Dictionary<Agent, Role>();
                if (!gameInfo.RoleMap.TryGetValue(a, out Role hisRole))
                {
                    hisRole = Role.UNC;
                }
                if (myRole == Role.WEREWOLF)
                {
                    if (hisRole == Role.WEREWOLF)
                    {
                        speciesMap[a] = Species.WEREWOLF;
                    }
                    else
                    {
                        speciesMap[a] = Species.HUMAN;
                    }
                }
                else
                {
                    speciesMap[a] = hisRole.GetSpecies();
                }
                statMap[a] = new UtteranceStatistics(0.0);
            }
            IsModified = true;
        }

        /// <summary>
        /// update of features
        /// </summary>
        /// <param name="gameInfo"></param>
        /// <param name="isDebug">true if output unparsable utterance to stderr</param>
        /// <returns>false if failed to update</returns>
        public bool Update(IGameInfo gameInfo, bool isDebug)
        {
            if (gameInfo.Day < date || gameInfo.StatusMap[me] == Status.DEAD)
            {
                return false;
            }

            Dictionary<Agent, AgentFeature> oldFeatureMap = new Dictionary<Agent, AgentFeature>();
            foreach (var p in featureMap)
            {
                oldFeatureMap[p.Key] = p.Value.Clone;
            }

            if (gameInfo.Day > date)
            {
                date = gameInfo.Day;
                foreach (var a in gameInfo.AgentList)
                {
                    featureMap[a][IsDead] = gameInfo.StatusMap[a] == Status.ALIVE ? 0 : 1;
                }
                foreach (var vote in gameInfo.VoteList)
                {
                    var voter = vote.Agent;
                    if (votingMap.TryGetValue(voter, out Vote v) && vote.Day == v.Day && vote.Target != v.Target)
                    {
                        featureMap[voter][NumChangeVote]++;
                    }
                }
#nullable disable
                if (gameInfo.DivineResult != null)
                {
                    speciesMap[gameInfo.DivineResult.Target] = gameInfo.DivineResult.Result;
                }
                if (gameInfo.MediumResult != null)
                {
                    speciesMap[gameInfo.MediumResult.Target] = gameInfo.MediumResult.Result;
                }
                if (gameInfo.ExecutedAgent != null)
                {
                    featureMap[gameInfo.ExecutedAgent][IsExecuted] = 1;
                }
#nullable restore
                foreach (var a in gameInfo.LastDeadAgentList)
                {
                    featureMap[a][IsKilled] = 1;
                    speciesMap[a] = Species.HUMAN;
                }
                talkListHead = 0;
                votingMap.Clear();
            }

            for (var i = talkListHead; i < gameInfo.TalkList.Count; i++)
            {
                var talk = gameInfo.TalkList[i];
                var content = new Content(talk);
                if (!ParseSentence(content) && isDebug)
                {
                    Console.Error.WriteLine(content);
                }
            }
            talkListHead = gameInfo.TalkList.Count;

            foreach (var a in gameInfo.AgentList)
            {
                featureMap[a][NumJudgedAsWhite] = 0;
                featureMap[a][NumJudgedAsBlack] = 0;
                featureMap[a][NumWhiteJudgement] = 0;
                featureMap[a][NumBlackJudgement] = 0;
            }
            foreach (var agent in divinationMap.Keys)
            {
                foreach (var target in divinationMap[agent].Keys)
                {
                    var result = divinationMap[agent][target];
                    if (result == Species.HUMAN)
                    {
                        featureMap[target][NumJudgedAsWhite]++;
                        featureMap[agent][NumWhiteJudgement]++;
                        if (target == me)
                        {
                            featureMap[agent][IsAlly] = 1;
                        }
                        if (speciesMap[target] == Species.WEREWOLF)
                        {
                            featureMap[agent][IsEnemy] = 1;
                        }
                    }
                    else if (result == Species.WEREWOLF)
                    {
                        featureMap[target][NumJudgedAsBlack]++;
                        featureMap[agent][NumBlackJudgement]++;
                        if (target == me)
                        {
                            featureMap[agent][IsEnemy] = 1;
                        }
                        if (speciesMap[target] == Species.HUMAN)
                        {
                            featureMap[agent][IsEnemy] = 1;
                        }
                    }
                }
            }
            foreach (var agent in identMap.Keys)
            {
                foreach (var target in identMap[agent].Keys)
                {
                    var result = identMap[agent][target];
                    if ((result == Species.WEREWOLF && speciesMap[target] == Species.HUMAN) || (result == Species.HUMAN && speciesMap[target] == Species.WEREWOLF))
                    {
                        featureMap[agent][IsEnemy] = 1;
                    }
                }
            }
            foreach (var p in speciesMap)
            {
                if (p.Value == Species.HUMAN)
                {
                    featureMap[p.Key][IsHuman] = 1;
                }
                else if (p.Value == Species.WEREWOLF)
                {
                    featureMap[p.Key][IsWerewolf] = 1;
                }
            }

            IsModified = IsModified || featureMap.Any(p => !p.Value.Equals(oldFeatureMap[p.Key]));
            return true;
        }

        void UpdateStatMap(Content content)
        {
            if (content.Date != 1)
            {
                return;
            }
            IsModified = statMap[content.Talker].Set(content.Turn, content.Topic, 1);
        }

        bool ParseSentence(Content content)
        {
            if (content.Topic == Topic.Skip || content.Topic == Topic.Over)
            {
                UpdateStatMap(content);
                return true;
            }
            return AddCo(content) || AddDivined(content) || AddIdentified(content) || AddVote(content) || AddEstimate(content) || ParseOperator(content);
        }

        bool ParseOperator(Content content)
        {
            if (content.Topic == Topic.OPERATOR)
            {
                UpdateStatMap(content);
                return ParseBecause(content) || ParseDay(content) || ParseAnd(content) || ParseOr(content) || ParseXor(content) || ParseRequset(content) || ParseInquire(content);
            }
            return false;
        }

        bool ParseBecause(Content content)
        {
            if (content.Operator == Operator.BECAUSE)
            {
                var subTalk = new Talk(content.Index, content.Date, content.Turn, content.Talker, content.ContentList[1].Text);
                return ParseSentence(new Content(subTalk));
            }
            return false;
        }

        bool ParseDay(Content content)
        {
            if (content.Operator == Operator.DAY)
            {
                var subTalk = new Talk(content.Index, content.Date, content.Turn, content.Talker, content.ContentList[0].Text);
                return ParseSentence(new Content(subTalk));
            }
            return false;
        }

        bool ParseAnd(Content content)
        {
            if (content.Operator == Operator.AND)
            {
                return content.ContentList.All(c => ParseSentence(new Content(new Talk(content.Index, content.Date, content.Turn, content.Talker, c.Text))));
            }
            return false;
        }

        bool ParseOr(Content content)
        {
            if (content.Operator == Operator.OR)
            {
                return content.ContentList.All(c => c.Topic == Topic.VOTE && ParseSentence(new Content(new Talk(content.Index, content.Date, content.Turn, content.Talker, c.Text))));
            }
            return false;
        }

        bool ParseXor(Content content)
        {
            if (content.Operator == Operator.XOR)
            {
                return content.ContentList.All(c => (c.Topic == Topic.VOTE || c.Topic == Topic.ESTIMATE)
                        && ParseSentence(new Content(new Talk(content.Index, content.Date, content.Turn, content.Talker, c.Text))));
            }
            return false;
        }

        bool ParseRequset(Content content)
        {
            if (content.Operator == Operator.REQUEST)
            {
                return true;
            }
            return false;
        }

        bool ParseInquire(Content content)
        {
            if (content.Operator == Operator.INQUIRE)
            {
                return true;
            }
            return false;
        }

        /// <summary>
        /// 
        /// </summary>
        /// <param name="agent"></param>
        /// <returns></returns>
        public double[] GetFeatureArrayOf(Agent agent)
        {
            List<double[]> dList = new List<double[]>
            {
                new double[] { date },
                RoleVectorMap[myRole],
                featureMap[me].ToArray(),
                featureMap[agent].ToArray()
            };
            List<AgentFeature> agentFeatureList = new List<AgentFeature>();
            foreach (var a in featureMap.Keys)
            {
                if (a != me && a != agent)
                {
                    agentFeatureList.Add(featureMap[a]);
                }
            }
            foreach (var f in agentFeatureList) // とりあえず特徴量エンジニアリングなし
            {
                dList.Add(f.ToArray());
            }
            return dList.SelectMany(d => d).ToArray();
        }

        /// <summary>
        /// 
        /// </summary>
        /// <param name="agent"></param>
        /// <returns></returns>
        public double[] GetUtterancePatternOf(Agent agent)
        {
            return statMap[agent].AbsoluteVector;
        }

        /// <summary>
        /// 
        /// </summary>
        /// <param name="agent"></param>
        /// <returns></returns>
        public double[,] GetUtteranceMatrixOf(Agent agent)
        {
            return statMap[agent].AbsoluteMatrix;
        }

        bool AddCo(Content content)
        {
            if (content.Topic == Topic.COMINGOUT && content.Subject == content.Target)
            {
                UpdateStatMap(content);
                AddCo(content.Subject, content.Role);
                return true;
            }
            return false;
        }

        void AddCo(Agent talker, Role coRole)
        {
            comingoutMap[talker] = coRole;
            switch (coRole)
            {
                case Role.WEREWOLF:
                    featureMap[talker][CoWerewolf] = 1;
                    break;
                case Role.VILLAGER:
                    featureMap[talker][CoVillager] = 1;
                    break;
                case Role.SEER:
                    featureMap[talker][CoSeer] = 1;
                    if (myRole == Role.SEER && talker != me)
                    {
                        featureMap[talker][IsEnemy] = 1;
                    }
                    break;
                case Role.POSSESSED:
                    featureMap[talker][CoPossessed] = 1;
                    break;
                case Role.MEDIUM:
                    featureMap[talker][CoMedium] = 1;
                    if (myRole == Role.MEDIUM && talker != me)
                    {
                        featureMap[talker][IsEnemy] = 1;
                    }
                    break;
                case Role.BODYGUARD:
                    featureMap[talker][CoBodyguard] = 1;
                    break;
                default:
                    break;
            }
        }

        bool AddDivined(Content content)
        {
            if (content.Topic == Topic.DIVINED)
            {
                UpdateStatMap(content);
                AddDivined(content.Subject, content.Target, content.Result);
                return true;
            }
            return false;
        }

        void AddDivined(Agent talker, Agent target, Species result)
        {
            AddCo(talker, Role.SEER);
            divinationMap[talker][target] = result;
        }

        bool AddIdentified(Content content)
        {
            if (content.Topic == Topic.IDENTIFIED)
            {
                UpdateStatMap(content);
                AddIdentified(content.Subject, content.Target, content.Result);
                return true;
            }
            return false;
        }

        void AddIdentified(Agent talker, Agent target, Species result)
        {
            AddCo(talker, Role.MEDIUM);
            identMap[talker][target] = result;
        }

        bool AddVote(Content content)
        {
            if (content.Topic == Topic.VOTE)
            {
                UpdateStatMap(content);
                votingMap[content.Subject] = new Vote(date, content.Subject, content.Target);
                return true;
            }
            return false;
        }

        bool AddEstimate(Content content)
        {
            if (content.Topic == Topic.ESTIMATE)
            {
                UpdateStatMap(content);
                estimateMap[content.Subject][content.Target] = content.Role;
                return true;
            }
            return false;
        }

        class Content : AIWolf.Lib.Content
        {
            public Agent Talker { get; }

            public int Index { get; }

            public int Date { get; }

            public int Turn { get; }

            public Content(Talk talk)
                : base((talk.Text == Talk.SKIP || talk.Text == Talk.OVER ? "" : talk.Agent.ToString()) + StripSubject(talk.Text))
            {
                Talker = talk.Agent;
                Index = talk.Idx;
                Date = talk.Day;
                Turn = talk.Turn;
            }
        }
    }
}
