/*
    Written in C++ for faster hyperparams search.
*/

#include <iostream>
#include <cstring>
#include <algorithm>
#include <fstream>
#include <map>

#include <boost/locale.hpp>

using namespace std;

const string TEXTS_FILE = "wp.inputs.txt";
const string TAGS_FILE = "wp.outputs.txt";
const string TITLES_FILE = "wp.titles.txt";

const int32_t HYPERPARAMS_NUM = 5;

boost::locale::generator gen;
std::locale global(gen(""));

class TDatasetText {
private:
    string Title;
    vector<string> TokenizedTitle;
    vector<string> ActualTags;
    vector<string> TokenizedText;

    vector<string> Split(const string& s, const string sep = " ") const {
        string currentStr = "";
        vector<string> result;
        for (char c : s) {
            if (sep.find(c) == string::npos) {
                currentStr += c;
            } else {
                if (currentStr > "") {
                    result.push_back(std::move(currentStr));
                    currentStr = "";
                }
            }
        }
        if (currentStr > "") {
            result.push_back(std::move(currentStr));
        }
        return result;
    }

    vector<string> Tokenize (const string& s, const string& punctuation = ".?!,;:-", const string& quotes="\"'<>()[]{}") const {
        vector<string> rawTokens = Split(s, "  \t\n");
        vector<string> result;
        for (auto&& token : rawTokens) {
            bool hasSeparatorAfter = false;
            while (token.size() > 0 && punctuation.find(token[token.size() - 1]) != string::npos) {
                hasSeparatorAfter = true;
                token.erase(token.size() - 1, 1);
            }
            while (token.size() > 0 && quotes.find(token[token.size() - 1]) != string::npos) {
                token.erase(token.size() - 1, 1);
            }
            while (token.size() > 0 && quotes.find(token[0]) != string::npos) {
                token.erase(0, 1);
            }
            if (token.size() > 0) {
                result.push_back(std::move(token));
            }
            if (hasSeparatorAfter && (result.size() == 0 || result.back() != ".")) {
                result.push_back(".");
            }
        }
        return result;
    }

public:

    TDatasetText(const string& title, const string& actualTags, const string& text) {
        Title = boost::locale::to_lower(title, global);
        TokenizedTitle = std::move(Tokenize(boost::locale::to_lower(title, global)));
        TokenizedText = std::move(Tokenize(boost::locale::to_lower(text, global)));

        ActualTags.clear();
        for (auto&& tag : Split(actualTags, "\t")) {
            tag = boost::locale::to_lower(tag, global);
            if (tag.size() > 0 && tag[0] == '#') {
                tag = tag.substr(1, tag.size() - 1);
            }
            ActualTags.push_back(std::move(tag));
        }
    }
    
    vector<string> GetTokenizedText() const {
        return TokenizedText;
    }

    vector<string> GetActualKeywords() const {
        return ActualTags;
    }

    vector<string> GetTokenizedTitle() const {
        return TokenizedTitle;
    }
};

class TParamsOptimizer {
private:
    vector<TDatasetText> Texts;

    vector<string> GetPredictedKeywords(const TDatasetText& text, const int32_t* hyperparams, const size_t bestK = 9) const {
        map<string, uint32_t> candidateOccurrence;
        map<string, uint32_t> candidateFirstOccurrencePosition;
        map<string, uint32_t> candidateTitleOccurrence;
        for (int32_t ngramLength = 1; ngramLength <= 3; ++ngramLength) {
            auto tkText = text.GetTokenizedText();
            for (int32_t firstWordIdx = 0; firstWordIdx < (int32_t)tkText.size() - ngramLength + 1; ++firstWordIdx) {
                string candidate = "";
                bool hasSeparator = false;
                for (size_t i = 0; i < ngramLength; ++i) {
                    if (tkText[firstWordIdx + i] == ".") {
                        hasSeparator = true;
                        break;
                    }
                    if (candidate.size() > 0) {
                        candidate += " ";
                    }
                    candidate += tkText[firstWordIdx + i];
                }
                if (hasSeparator) {
                    continue;
                }
                if (!candidateOccurrence.count(candidate)) {
                    candidateOccurrence[candidate] = 0;
                    candidateFirstOccurrencePosition[candidate] = firstWordIdx;
                    candidateTitleOccurrence[candidate] = 0;
                    auto titleTokens = text.GetTokenizedTitle();
                    for (int32_t i = 0; i < (int32_t)titleTokens.size() - (int32_t)ngramLength + 1; ++i) {
                        string titleSubstring = "";
                        for (size_t j = 0; j < ngramLength; ++j) {
                            if (titleSubstring > "") {
                                titleSubstring += " ";
                            }
                            titleSubstring += titleTokens[i + j];
                        }
                        if (titleSubstring == candidate) {
                            ++candidateTitleOccurrence[candidate];
                        }
                    }
                }
                ++candidateOccurrence[candidate];
            }
        }
        //
        set<string> processedCandidates;
        vector<pair<int64_t, string>> scores;
        for (int32_t ngramLength = 1; ngramLength <= 3; ++ngramLength) {
            auto tkText = text.GetTokenizedText();
            for (int32_t firstWordIdx = 0; firstWordIdx < (int32_t)tkText.size() - ngramLength + 1; ++firstWordIdx) {
                string candidate = "";
                bool hasSeparator = false;
                for (int32_t i = 0; i < ngramLength; ++i) {
                    if (tkText[firstWordIdx + i] == ".") {
                        hasSeparator = true;
                        break;
                    }
                    if (candidate.size() > 0) {
                        candidate += " ";
                    }
                    candidate += tkText[firstWordIdx + i];
                }
                if (hasSeparator || processedCandidates.find(candidate) != processedCandidates.end()) {
                    continue;
                }
                uint64_t candidateScore = candidateOccurrence[candidate] * hyperparams[0];
                candidateScore += candidateTitleOccurrence[candidate] * hyperparams[1];
                candidateScore += candidateFirstOccurrencePosition[candidate] * -hyperparams[2];
                if (ngramLength > 1) {
                    for (size_t i = 0; i < ngramLength; ++i) {
                        auto& word = tkText[firstWordIdx + i];
                        candidateScore += candidateOccurrence[word] * hyperparams[1 + ngramLength];
                    }
                }
                processedCandidates.insert(candidate);
                scores.push_back(make_pair(candidateScore, candidate));
            }
        }
        //
        sort(scores.begin(), scores.end());
        reverse(scores.begin(), scores.end());
        vector<string> result;
        for (size_t i = 0; i < min(bestK, scores.size()); ++i) {
            result.push_back(scores[i].second);
        }
        return result;
    }

    int64_t CalculateTextScore(const TDatasetText& text, const int32_t* hyperparams) const {
        auto keywords = GetPredictedKeywords(text, hyperparams);
        set<string> actualKeywords;
        for (auto& keyword : text.GetActualKeywords()) {
            actualKeywords.insert(keyword);
        }
        int32_t result = 0;
        for (auto& keyword : keywords) {
            if (actualKeywords.find(keyword) != actualKeywords.end()) {
                ++result;
            }
        }
        return result;
    }

    int64_t CalculateScore(const int32_t* hyperparams) const {
        int64_t result = 0;
        for (size_t i = 0; i < Texts.size(); ++i) {
            result += CalculateTextScore(Texts[i], hyperparams);
        }
        return result;
    }

public:

    void ReadInputData(const string& textsFilename = TEXTS_FILE, const string& tagsFilename = TAGS_FILE, const string& titlesFilename = TITLES_FILE) {
        fstream textsFile(textsFilename);
        fstream tagsFile(tagsFilename);
        fstream titlesFile(titlesFilename);

        string currentText;
        string currentTags;
        string currentTitle;
        while (getline(textsFile, currentText)) {
            getline(tagsFile, currentTags);
            getline(titlesFile, currentTitle);
            Texts.push_back(TDatasetText(currentTitle, currentTags, currentText));
        }

        textsFile.close();
        tagsFile.close();
        titlesFile.close();
    }

    void RandomHyperparametersSearch() const {
        int32_t bestHyperParams[HYPERPARAMS_NUM];
        bestHyperParams[0] = 100;  // weight per occurrence
        bestHyperParams[1] = 200;  // weight per occurrence in title
        bestHyperParams[2] = 4;  // penalty per first occurence position
        bestHyperParams[3] = 0;  // bonus for partial occurrence in 2-gram
        bestHyperParams[4] = 0;  // bonus for partial occurrence in 3-gram
        int64_t bestScore = CalculateScore(bestHyperParams);
        cerr << "The current best score is: " << bestScore << endl;
        return ;
        while (true) {
            int32_t newHyperParams[HYPERPARAMS_NUM];
            for (size_t i = 0; i < HYPERPARAMS_NUM; ++i) {
                newHyperParams[i] = rand() % 1000;
            }
            int64_t newScore = CalculateScore(newHyperParams);
            if (newScore > bestScore) {
                bestScore = newScore;
                for (size_t i = 0; i < HYPERPARAMS_NUM; ++i) {
                    bestHyperParams[i] = newHyperParams[i];
                }
            }
        }
    }

} optimizer;

int main () {
    optimizer.ReadInputData();
    optimizer.RandomHyperparametersSearch();
    return 0;
}

