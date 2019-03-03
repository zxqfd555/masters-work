function tokenizeText(text, stoplist) {
    var punctuationsStr = ".?!,;:-";
    var quotesStr = "\"'<>()[]{}";

    var textLength = text.length;
    var currentWord = "";
    var rawTokens = text.split("\n").join(" ").split("\t").join(" ").split(" ");
    var result = [];

    for (var i = 0; i < rawTokens.length; ++i) {
        var token = rawTokens[i];
        var hasSeparatorAfter = false;
        while (token.length > 0 && punctuationsStr.indexOf(token[token.length - 1]) != -1) {
            token = token.substring(0, token.length - 1);
            hasSeparatorAfter = true;
        }
        while (token.length > 0 && quotesStr.indexOf(token[token.length - 1]) != -1) {
            token = token.substring(0, token.length - 1);
        }
        while (token.length > 0 && quotesStr.indexOf(token[0]) != -1) {
            token = token.substring(1, token.length - 1);
        }
        token = token.toLowerCase();
        if (token.length >= 2 && token[token.length - 2] == "'" && token[token.length - 1] == "s") {
            token = token.substring(0, token.length - 2);
        }
        if (token.length > 0) {
            if (stoplist.has(token)) {
                result.push(".");
            } else {
                result.push(token);
            }
        }
        if (hasSeparatorAfter && (result.length == 0 || result[result.length - 1] != ".")) {
            result.push(".");
        }
    }

    return result;
}

function buildCandidates(titleTokens, textTokens) {

    // Calculate stats
    
    console.log("hi");

    var candidateOccurrence = {};
    var candidateTitleOccurrence = {};
    var candidateFirstOccurrencePosition = {};
    for (var windowSize = 1; windowSize <= 3; ++windowSize) {
        for (var firstWordIdx = 0; firstWordIdx < textTokens.length - windowSize + 1; ++firstWordIdx) {
            var candidate = "";
            var hasSeparator = false;
            for (var i = 0; i < windowSize; ++i) {
                if (candidate != "") {
                    candidate += " ";
                }
                if (textTokens[firstWordIdx + i] == ".") {
                    hasSeparator = true;
                    break;
                }
                candidate += textTokens[firstWordIdx + i];
            }
            if (hasSeparator) {
                continue;
            }
            if (!(candidate in candidateOccurrence)) {
                candidateOccurrence[candidate] = 0;
                candidateTitleOccurrence[candidate] = 0;
                candidateFirstOccurrencePosition[candidate] = firstWordIdx;
                for (var i = 0; i < titleTokens.length - windowSize + 1; ++i) {
                    var isMatching = true;
                    for (var j = 0; j < windowSize; ++j) {
                        if (titleTokens[i + j] != textTokens[firstWordIdx + j]) {
                            isMatching = false;
                            break;
                        }
                    }
                    if (isMatching) {
                        candidateTitleOccurrence[candidate] = candidateTitleOccurrence[candidate] + 1;
                    }
                }
            }
            candidateOccurrence[candidate] = candidateOccurrence[candidate] + 1;
        }
    }

    // Build candidates
    var processedCandidates = new Set;
    var candidates = [];

    for (var windowSize = 1; windowSize <= 3; ++windowSize) {
        for (var firstWordIdx = 0; firstWordIdx < textTokens.length - windowSize + 1; ++firstWordIdx) {
            var candidate = "";
            var hasSeparator = false;
            for (var i = 0; i < windowSize; ++i) {
                if (candidate != "") {
                    candidate += " ";
                }
                if (textTokens[firstWordIdx + i] == ".") {
                    hasSeparator = true;
                    break;
                }
                candidate += textTokens[firstWordIdx + i];
            }
            if (hasSeparator || processedCandidates.has(candidate)) {
                continue;
            }
            processedCandidates.add(candidate);

            var C1 = 0;
            var C2 = 0;
            for (var i = 0; i < windowSize; ++i) {
                var subword = textTokens[firstWordIdx + i];
                if (windowSize == 2) {
                    C1 += candidateOccurrence[subword];
                } else if (windowSize == 3) {
                    C2 += candidateOccurrence[subword];
                }
            }

            candidateScore = (
                5.63055325e-01 * candidateOccurrence[candidate] +
                2.73927772e+00 * candidateTitleOccurrence[candidate] -
                8.59746376e-04 * candidateFirstOccurrencePosition[candidate] +
                7.66210243e-02 * C1 +
                2.08424009e-02 * C2
            );

            candidates.push([candidateScore, candidate]);
        }
    }

    return candidates;
}

function compareCandidates(a, b) {
    if (a[0] < b[0]) {
        return 1;
    } else if (a[0] > b[0]) {
        return -1;
    }
    return 0;
}

function generateTags(title, text) {
    var titleTokens = tokenizeText(text, getFoxStoplist());
    var textTokens = tokenizeText(text, getFoxStoplist());

    var weightedCandidates = buildCandidates(titleTokens, textTokens);
    weightedCandidates.sort(compareCandidates);
    
    var result = [];
    var resultSize = 10;
    if (resultSize > weightedCandidates.length) {
        resultSize = weightedCandidates.length;
    }
    for (var i = 0; i < resultSize; ++i) {
        result.push(weightedCandidates[i][1]);
    }

    return result;
}

