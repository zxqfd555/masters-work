/*
    Written in C++ for faster hyperparams search.
*/

#include <iostream>
#include <cstring>
#include <algorithm>
#include <fstream>

#include <boost/locale.hpp>

using namespace std;

const string TEXTS_FILE = "wp.inputs.txt";
const string TAGS_FILE = "wp.outputs.txt";
const string TITLES_FILE = "wp.titles.txt";

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
};

class TParamsOptimizer {
private:
    vector<TDatasetText> Texts;

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

} optimizer;

int main () {
    optimizer.ReadInputData();
    return 0;
}

