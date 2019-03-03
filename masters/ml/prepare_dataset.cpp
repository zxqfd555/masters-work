#include <iostream>
#include <cstring>
#include <algorithm>
#include <vector>
#include <fstream>
#include <map>

#include <boost/locale.hpp>

using namespace std;

const string TEXTS_FILE = "wp.inputs.txt";
const string TAGS_FILE = "wp.outputs.txt";
const string TITLES_FILE = "wp.titles.txt";
const string STOPWORDS_FILE = "FoxStoplist.txt";

const int32_t HYPERPARAMS_NUM = 5;

boost::locale::generator gen;
std::locale global(gen(""));

set<string> STOP_WORDS_SET;

class TDatasetText {
private:
    string Title;
    vector<string> TokenizedTitle;
    vector<string> ActualTags;
    vector<string> TokenizedText;

    vector<pair<string, int32_t*> > CandidateFeatures;

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
                if (STOP_WORDS_SET.find(token) != STOP_WORDS_SET.end()) {
                    result.push_back(".");
                } else {
                    result.push_back(std::move(token));
                }
            }
            if (hasSeparatorAfter && (result.size() == 0 || result.back() != ".")) {
                result.push_back(".");
            }
        }
        return result;
    }

    void PrecalculateFeatures () {
        map<string, int32_t> candidateOccurrence;
        map<string, int32_t> candidateTitleOccurrence;
        map<string, int32_t> candidateFirstOccurrencePosition;
        for (int32_t ngramLength = 1; ngramLength <= 3; ++ngramLength) {
            for (int32_t firstWordIdx = 0; firstWordIdx < (int32_t)TokenizedText.size() - ngramLength + 1; ++firstWordIdx) {
                string candidate = "";
                bool hasSeparator = false;
                for (size_t i = 0; i < ngramLength; ++i) {
                    if (TokenizedText[firstWordIdx + i] == ".") {
                        hasSeparator = true;
                        break;
                    }
                    if (candidate.size() > 0) {
                        candidate += " ";
                    }
                    candidate += TokenizedText[firstWordIdx + i];
                }
                if (hasSeparator) {
                    continue;
                }
                if (!candidateOccurrence.count(candidate)) {
                    candidateOccurrence[candidate] = 0;
                    candidateFirstOccurrencePosition[candidate] = firstWordIdx;
                    candidateTitleOccurrence[candidate] = 0;
                    for (int32_t i = 0; i < (int32_t)TokenizedTitle.size() - (int32_t)ngramLength + 1; ++i) {
                        string titleSubstring = "";
                        for (size_t j = 0; j < ngramLength; ++j) {
                            if (titleSubstring > "") {
                                titleSubstring += " ";
                            }
                            titleSubstring += TokenizedTitle[i + j];
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
            for (int32_t firstWordIdx = 0; firstWordIdx < (int32_t)TokenizedText.size() - ngramLength + 1; ++firstWordIdx) {
                string candidate = "";
                bool hasSeparator = false;
                for (int32_t i = 0; i < ngramLength; ++i) {
                    if (TokenizedText[firstWordIdx + i] == ".") {
                        hasSeparator = true;
                        break;
                    }
                    if (candidate.size() > 0) {
                        candidate += " ";
                    }
                    candidate += TokenizedText[firstWordIdx + i];
                }
                if (hasSeparator || processedCandidates.find(candidate) != processedCandidates.end()) {
                    continue;
                }

                auto features = new int32_t[HYPERPARAMS_NUM];
                features[0] = candidateOccurrence[candidate];
                features[1] = candidateTitleOccurrence[candidate];
                features[2] = -candidateFirstOccurrencePosition[candidate];
                features[3] = 0;
                features[4] = 0;
                if (ngramLength > 1) {
                    for (size_t i = 0; i < ngramLength; ++i) {
                        auto& word = TokenizedText[firstWordIdx + i];
                        features[1 + ngramLength] += candidateOccurrence[word];
                    }
                }
                processedCandidates.insert(candidate);
                CandidateFeatures.push_back(make_pair(candidate, features));
            }
        }
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

        PrecalculateFeatures();
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

    vector<pair<string, int32_t*>>& GetCandidateFeatures() {
        return CandidateFeatures;
    }

    void DumpFeatures(ostream& os, int label = -1) {
        set<string> actualTagsSet;
        for (auto&& tag : ActualTags) {
            actualTagsSet.insert(tag);
        }

        bool isNeeded = false;
        for (auto&& element : CandidateFeatures) {
            bool isTag = actualTagsSet.find(element.first) != actualTagsSet.end();
            isNeeded |= isTag;
        }

        if (!isNeeded) {
            return;
        }

        for (auto&& element : CandidateFeatures) {
            bool isTag = actualTagsSet.find(element.first) != actualTagsSet.end();
            for (size_t featureIdx = 0; featureIdx < HYPERPARAMS_NUM; ++featureIdx) {
                os << element.second[featureIdx] << " ";
            }
            os << TokenizedText.size() << " " << isTag;
            if (label != -1) {
                os << " " << label;
            }
            os << endl;
        }
    }
};

class TParamsOptimizer {
private:
    vector<TDatasetText> Texts;
    size_t TrainingSetSize = 0;
    bool IsVerbose = false;

    int64_t GridSearchBestScore;
    uint64_t GridSearchCombinationsProcessed;
    clock_t GridSearchStartTime;

    class THyperParameter {
    private:
        int32_t StartValue;
        int32_t EndValue;
        int32_t Step;

    public:
        THyperParameter() = default;

        THyperParameter(const int32_t startValue, const int32_t endValue, const int32_t step)
            : StartValue(startValue)
            , EndValue(endValue)
            , Step(step)
        {
        }

        int32_t GetStartValue() const {
            return StartValue;
        }

        int32_t GetEndValue() const {
            return EndValue;
        }

        int32_t GetStep() const {
            return Step;
        }
        
        uint64_t GetCombinationsNumber() const {
            int64_t range = (EndValue - StartValue) / Step + 1;
            if (range < 0) {
                return 0;
            } else {
                return range;
            }
        }
    };

    vector<string> GetPredictedKeywords(TDatasetText& text, const int32_t* hyperparams, const size_t bestK = 9) {
        vector<pair<int64_t, string>> scores;
        for (auto candidate : text.GetCandidateFeatures()) {
            int32_t score = 0;
            for (size_t i = 0; i < HYPERPARAMS_NUM; ++i) {
                score += hyperparams[i] * candidate.second[i];
            }
            scores.push_back(make_pair(score, candidate.first));
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

    int64_t CalculateTextScore(TDatasetText& text, const int32_t* hyperparams) {
        auto keywords = GetPredictedKeywords(text, hyperparams);
        set<string> actualKeywords;
        for (auto& keyword : text.GetActualKeywords()) {
            actualKeywords.insert(keyword);
        }
        int32_t result = 0;
        for (auto& keyword : keywords) {
            if (IsVerbose) {
                cerr << keyword << " | ";
            }
            if (actualKeywords.find(keyword) != actualKeywords.end()) {
                ++result;
            }
        }
        if (IsVerbose) {
            cerr << endl;
        }
        return result;
    }

    int64_t CalculateScore(const int32_t* hyperparams) {
        int64_t result = 0;

        size_t setSize;
        if (TrainingSetSize == 0) {
            setSize = Texts.size();
        } else {
            setSize = min(Texts.size(), TrainingSetSize);
        }

        for (size_t i = 0; i < setSize; ++i) {
            result += CalculateTextScore(Texts[i], hyperparams);
        }
        return result;
    }

    void DoGridSearch (THyperParameter* searchParams, size_t currentParamIndex, int32_t* currentHyperParams, int32_t* bestHyperParams, uint64_t totalCombinations) {
        if (currentParamIndex == HYPERPARAMS_NUM) {
            uint64_t score = CalculateScore(currentHyperParams);
            if (score > GridSearchBestScore) {
                GridSearchBestScore = score;
                cerr << "Best score updated to " << score << "! The hyperparams which led to this are:";
                for (size_t i = 0; i < HYPERPARAMS_NUM; ++i) {
                    bestHyperParams[i] = currentHyperParams[i];
                    cerr << " " << currentHyperParams[i];
                }
                cerr << endl;
            }
            ++GridSearchCombinationsProcessed;
            uint64_t onePercent = totalCombinations / 100;
            uint32_t percentDone = GridSearchCombinationsProcessed / onePercent;

            int32_t eta = (int)((clock() - GridSearchStartTime) / CLOCKS_PER_SEC) / percentDone * (100 - percentDone);

            if (GridSearchCombinationsProcessed % onePercent == 0) {
                cerr << "The job is " << GridSearchCombinationsProcessed / onePercent << "% completed. Estimated completion is in " << eta << " seconds." << endl;
            }
        } else {
            int32_t currentValue = searchParams[currentParamIndex].GetStartValue();
            while (currentValue <= searchParams[currentParamIndex].GetEndValue()) {
                currentHyperParams[currentParamIndex] = currentValue;
                currentValue += searchParams[currentParamIndex].GetStep();
                DoGridSearch(searchParams, currentParamIndex + 1, currentHyperParams, bestHyperParams, totalCombinations);
            }
        }
    }

public:

    void ReadInputData(
        const string& textsFilename = TEXTS_FILE, const string& tagsFilename = TAGS_FILE,
        const string& titlesFilename = TITLES_FILE, const string& stopwordsFilename = STOPWORDS_FILE
    ) {
        fstream textsFile(textsFilename);
        fstream tagsFile(tagsFilename);
        fstream titlesFile(titlesFilename);
        fstream stopwordsFile(stopwordsFilename);

        string currentStopWord;
        while (getline(stopwordsFile, currentStopWord)) {
            currentStopWord.erase(currentStopWord.size() - 1, 1);
            STOP_WORDS_SET.insert(boost::locale::to_lower(currentStopWord, global));
        }

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
        stopwordsFile.close();
        
        cerr << "Read completed" << endl;
        
//        ofstream featuresFile;
//        featuresFile.open("features-train.txt");
//        for (size_t i = 0; i < 1000; ++i) {
//            Texts[i].DumpFeatures(featuresFile);
//        }
//        featuresFile.close();

        ofstream featuresTestFile;
        featuresTestFile.open("test.txt");
        for (size_t i = 1000; i < Texts.size(); ++i) {
            Texts[i].DumpFeatures(featuresTestFile, i);
        }
        featuresTestFile.close();
    }

    void SetTrainingSetSize(size_t newSize) {
        TrainingSetSize = newSize;
    }

    void RandomHyperparametersSearch() {
        int32_t bestHyperParams[HYPERPARAMS_NUM];
        bestHyperParams[0] = 200;  // weight per occurrence
        bestHyperParams[1] = 1000;  // weight per occurrence in title
        bestHyperParams[2] = 1;  // penalty per first occurence position
        bestHyperParams[3] = 4;  // bonus for partial occurrence in 2-gram
        bestHyperParams[4] = 4;  // bonus for partial occurrence in 3-gram
        int64_t bestScore = CalculateScore(bestHyperParams);
        cerr << "The current best score is: " << bestScore << endl;
        while (true) {
            int32_t newHyperParams[HYPERPARAMS_NUM];
            
            newHyperParams[0] = rand() % 1000;
            newHyperParams[1] = rand() % 1000;
            newHyperParams[2] = rand() % 3;
            newHyperParams[3] = rand() % 100;
            newHyperParams[4] = rand() % 100;
            
            int64_t newScore = CalculateScore(newHyperParams);
            if (newScore > bestScore) {
                bestScore = newScore;
                for (size_t i = 0; i < HYPERPARAMS_NUM; ++i) {
                    bestHyperParams[i] = newHyperParams[i];
                }
                cerr << "The new best score is: " << bestScore << ". Hyperparams:";
                for (int i = 0; i < HYPERPARAMS_NUM; ++i) {
                    cerr << " " << bestHyperParams[i];
                }
                cerr << endl;
            }
        }
    }
    
    void GridHyperparametersSearch() {
        THyperParameter searchParams[HYPERPARAMS_NUM];
        searchParams[0] = THyperParameter(0, 1000, 100);
        searchParams[1] = THyperParameter(0, 2000, 200);
        searchParams[2] = THyperParameter(0, 5, 1);
        searchParams[3] = THyperParameter(0, 20, 4);
        searchParams[4] = THyperParameter(0, 20, 4);
        
        uint64_t combinationsNumber = 1;
        for (size_t i = 0; i < HYPERPARAMS_NUM; ++i) {
            combinationsNumber *= searchParams[i].GetCombinationsNumber();
        }
        cerr << "There are " << combinationsNumber << " steps, which are expected to be made" << endl;

        int32_t searchHyperParameters[HYPERPARAMS_NUM];
        int32_t bestHyperParameters[HYPERPARAMS_NUM];

        GridSearchStartTime = clock();
        GridSearchCombinationsProcessed = 0;
        GridSearchBestScore = 0;

        DoGridSearch(searchParams, 0, searchHyperParameters, bestHyperParameters, combinationsNumber);
        cerr << "Grid search finished" << endl;
    }

} optimizer;

int main () {
    optimizer.ReadInputData();
    return 0;
}

