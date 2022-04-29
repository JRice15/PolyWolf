//
// RoleEstimator.cs
//
// Copyright 2021 OTSUKI Takashi
// SPDX-License-Identifier: Apache-2.0
//

using AIWolf.Lib;
using OpenCvSharp;
using OpenCvSharp.Dnn;
using System;
using System.Collections.Generic;
using System.Linq;

namespace TOT2021
{
    /// <summary>
    /// Role estimator.
    /// </summary>
    class RoleEstimator : Dictionary<Agent, double>
    {
        int date;
        Role role;
        IGameInfo gameInfo = default!;
        Net[] model05;
        Net[] model15;
        Dictionary<Agent, Dictionary<Role, UtteranceStatistics>> statMap = new Dictionary<Agent, Dictionary<Role, UtteranceStatistics>>();
        Feature feature = default!;
        Dictionary<Agent, double> randomMap = new Dictionary<Agent, double>();

        Net LoadNN(int villageSize, Role role, int date)
        {
            var asm = System.Reflection.Assembly.GetExecutingAssembly();
            var rname = $"{asm.GetName().Name}.model{villageSize:00}.{role.ToString().ToLower()}.day{date:00}.bestModel.onnx";
            using (var stream = asm.GetManifestResourceStream(rname))
            {
                return CvDnn.ReadNetFromOnnx(stream)!;
            }
        }

        /// <summary>
        /// Constructs estimator for a role.
        /// </summary>
        /// <param name="role">The role.</param>
        public RoleEstimator(Role role)
        {
            this.role = role;
            // load models for 5 agent village
            model05 = new Net[4];
            if (role != Role.MEDIUM && role != Role.BODYGUARD)
            {
                for (var date = 1; date < 3; date++)
                {
                    model05[date] = LoadNN(5, role, date);
                }
            }
            model05[0] = model05[1];
            model05[3] = model05[2];

            // load models for 15 agent village
            model15 = new Net[15];
            for (var date = 1; date < 8; date++)
            {
                model15[date] = LoadNN(15, role, date);
            }
            model15[0] = model15[1];
            for (var date = 8; date < 15; date++)
            {
                model15[date] = model15[7];
            }

            for (var ai = 1; ai <= 15; ai++)
            {
                var map = new Dictionary<Role, UtteranceStatistics>();
                foreach (var r in new Role[] { Role.WEREWOLF, Role.VILLAGER, Role.SEER, Role.POSSESSED, Role.MEDIUM, Role.BODYGUARD })
                {
                    map[r] = new UtteranceStatistics(0.01);
                }
                statMap[Agent.GetAgent(ai)] = map;
            }
        }

        /// <summary>
        /// Initialize RoleEstimator using a GameInfo.
        /// </summary>
        /// <param name="gameInfo">The GameInfo.</param>
        public void Initialize(IGameInfo gameInfo)
        {
            var random = new Random();
            date = -1;
            foreach (var agent in gameInfo.AgentList)
            {
                if (agent == gameInfo.Agent && gameInfo.Role == role)
                {
                    this[agent] = 1.0;
                }
                else
                {
                    this[agent] = 0.0;
                }
                randomMap[agent] = random.NextDouble() / 1.0e7;
            }
            feature = new Feature(gameInfo);
        }

        /// <summary>
        /// Updates RoleEstimator using a GameInfo.
        /// </summary>
        /// <param name="gameInfo">The GameInfo.</param>
        public void Update(IGameInfo gameInfo)
        {
            this.gameInfo = gameInfo;
            date = gameInfo.Day;
            feature.Update(gameInfo, false);
            if (feature.IsModified)
            {
                UpdateValue();
            }
        }

        void UpdateValue()
        {
            foreach (var agent in gameInfo.AgentList)
            {
                if (agent == gameInfo.Agent)
                {
                    continue;
                }
                var f1 = new List<double[]>
                {
                    feature.GetFeatureArrayOf(agent)
                };
                foreach (var r in new Role[] { Role.WEREWOLF, Role.VILLAGER, Role.SEER, Role.POSSESSED, Role.MEDIUM, Role.BODYGUARD })
                {
                    double[] f2 = feature.GetUtterancePatternOf(agent);
                    double[] f3 = statMap[agent][r].RelativeVector;
                    double[] f4 = new double[f3.Length];
                    for (var i = 0; i < f3.Length; i++)
                    {
                        f4[i] = f2[i] * f3[i];
                    }
                    f1.Add(f4);
                }
                double[] f = f1.SelectMany(d => d).ToArray();
                var input = new Mat<double>(1, f.Length, f.ToArray());
                Net model = gameInfo.AgentList.Count == 5 ? model05[date] : model15[date];
                model.SetInput(input);
                this[agent] = model.Forward().Row(0).Get<float>(0) + randomMap[agent];
            }
        }

        /// <summary>
        /// Processing at the game end.
        /// </summary>
        public void Finish()
        {
            foreach (var agent in gameInfo.AgentList)
            {
                statMap[agent][gameInfo.RoleMap[agent]].Add(feature.GetUtteranceMatrixOf(agent));
            }
        }

        /// <summary>
        /// Returns the agent having maximum probability.
        /// </summary>
        /// <param name="agents">A list of candidates.</param>
        /// <param name="excludes">An array of agents excluded from candidates.</param>
        /// <returns>Agent.NONE if not found.</returns>
        public Agent Max(IEnumerable<Agent> agents, params Agent[] excludes)
            => Descneding(agents, excludes).DefaultIfEmpty(Agent.NONE).First();

        /// <summary>
        /// Returns the agent having minimum probability.
        /// </summary>
        /// <param name="agents">A list of candidates.</param>
        /// <param name="excludes">An array of agents excluded from candidates.</param>
        /// <returns>Agent.NONE if not found.</returns>
        public Agent Min(IEnumerable<Agent> agents, params Agent[] excludes)
            => Ascneding(agents, excludes).DefaultIfEmpty(Agent.NONE).First();

        /// <summary>
        /// Returns a list of agents sorted by role probability in descending order.
        /// </summary>
        /// <param name="agents">A list of agents to be sorted.</param>
        /// <param name="excludes">An array of agents excluded from the list.</param>
        /// <returns>A list of agents sorted by role probability in descending order.</returns>
        public List<Agent> Descneding(IEnumerable<Agent> agents, params Agent[] excludes)
            => agents.Where(a => !excludes.Contains(a)).OrderByDescending(a => this[a]).ToList();

        /// <summary>
        /// Returns a list of agents sorted by role probability in ascending order.
        /// </summary>
        /// <param name="agents">A list of agents to be sorted.</param>
        /// <param name="excludes">An array of agents excluded from the list.</param>
        /// <returns>A list of agents sorted by role probability in ascending order.</returns>
        public List<Agent> Ascneding(IEnumerable<Agent> agents, params Agent[] excludes)
            => agents.Where(a => !excludes.Contains(a)).OrderBy(a => this[a]).ToList();

    }
}
