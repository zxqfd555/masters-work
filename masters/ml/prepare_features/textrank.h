#pragma once

#include <cstring>
#include <vector>
#include <algorithm>

using namespace std;

namespace NTextRank {

    const int32_t WINDOW_SIZE = 2;

    struct TKeyword {
        string Value;
        double Rank;
        vector<double> ExtraFeatures;

        TKeyword() = default;
        
        TKeyword(const string& value, const double rank)
            : Value(value)
            , Rank(rank)
        {
        }
    };

    vector<TKeyword> GetKeywords(const vector<string>& tokenizedText, const size_t amount = 10, bool verbose = false) {
        size_t totalNodes = 0;

        map<string, size_t> wordToNode;
        vector<vector<size_t>> graph;
        for (size_t i = 0; i < tokenizedText.size(); ++i) {
            auto it = wordToNode.find(tokenizedText[i]);
            if (it == wordToNode.end()) {
                wordToNode.emplace(tokenizedText[i], totalNodes++);
            }
        }

        if (totalNodes == 0) {
            return vector<TKeyword>();
        }
        graph.resize(totalNodes);
        vector<int> outboundDegree(totalNodes, 0);
        for (size_t i = 0; i < tokenizedText.size() - 1; ++i) {
            for (size_t j = 1; j <= WINDOW_SIZE; ++j) {
                if (i + j < tokenizedText.size()) {
                    size_t origin = wordToNode[tokenizedText[i]];
                    size_t destination = wordToNode[tokenizedText[i + j]];
                    graph[destination].push_back(origin);
                    ++outboundDegree[origin];
                }

                if (i >= j) {
                    size_t origin = wordToNode[tokenizedText[i - j]];
                    size_t destination = wordToNode[tokenizedText[i]];
                    graph[destination].push_back(origin);
                    ++outboundDegree[origin];
                }
            }
        }

        vector<double> score(totalNodes, 1.0 / totalNodes);
        vector<double> newScore(totalNodes, 0.0);

        for(int it = 0; it < 40; it++) {
            for(int i = 0; i < totalNodes; i++) {
                newScore[i] = 0.0;
            }
            for(int i = 0; i < totalNodes; i++) {
                for(int node : graph[i]) {
                    newScore[i] += score[node] / (double)(outboundDegree[node]);
                }
            }
            for(int i = 0; i < totalNodes; i++) {
                score[i] = newScore[i];
            }
        }

        vector<TKeyword> candidates;
        for (auto&& it : wordToNode) {
            candidates.emplace_back(TKeyword(it.first, score[wordToNode[it.first]]));
        }
        sort(candidates.begin(), candidates.end(), [](const TKeyword& lhs, const TKeyword& rhs){return lhs.Rank > rhs.Rank;});
        if (candidates.size() > amount) {
            candidates.resize(amount);
        }

        if (verbose) {
            for (auto&& element : candidates) {
                cerr << element.Value << " " << element.Rank << endl;
            }
        }

        return candidates;
    }
};

