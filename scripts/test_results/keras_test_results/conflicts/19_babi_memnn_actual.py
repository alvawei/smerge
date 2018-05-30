from __future__ import print_function
from __future__ import print_function
from keras.models import Sequential
from keras.models import Sequential
from keras.layers.embeddings import Embedding
from keras.layers.embeddings import Embedding
from keras.layers.core import Activation, Dense, Merge, Permute, Dropout
from keras.layers.core import Activation, Dense, Merge, Permute, Dropout
from keras.layers.recurrent import LSTM
from keras.layers.recurrent import LSTM
from keras.datasets.data_utils import get_file
from keras.datasets.data_utils import get_file
from keras.preprocessing.sequence import pad_sequences
from keras.preprocessing.sequence import pad_sequences
from functools import reduce
import tarfile
import numpy as np
import tarfile
import numpy as np
import re
<<<<<<< REMOTE
import re
=======

>>>>>>> LOCAL
<<<<<<< REMOTE

=======
"""
Train a memory network on the bAbI dataset.

References:
- Jason Weston, Antoine Bordes, Sumit Chopra, Tomas Mikolov, Alexander M. Rush,
  "Towards AI-Complete Question Answering: A Set of Prerequisite Toy Tasks",
  http://arxiv.org/abs/1503.08895

- Sainbayar Sukhbaatar, Arthur Szlam, Jason Weston, Rob Fergus,
  "End-To-End Memory Networks",
  http://arxiv.org/abs/1503.08895

Reaches 93% accuracy on task 'single_supporting_fact_10k' after 70 epochs.
Time per epoch: 3s on CPU (core i7).
"""
>>>>>>> LOCAL
<<<<<<< REMOTE
"""
Train a memory network on the bAbI dataset.

References:
- Jason Weston, Antoine Bordes, Sumit Chopra, Tomas Mikolov, Alexander M. Rush,
  "Towards AI-Complete Question Answering: A Set of Prerequisite Toy Tasks",
  http://arxiv.org/abs/1503.08895

- Sainbayar Sukhbaatar, Arthur Szlam, Jason Weston, Rob Fergus,
  "End-To-End Memory Networks",
  http://arxiv.org/abs/1503.08895

Reaches 93% accuracy on task 'single_supporting_fact_10k' after 70 epochs.
Time per epoch: 3s on CPU (core i7).
"""
=======

>>>>>>> LOCAL

<<<<<<< REMOTE

=======
def tokenize(sent):
    '''Return the tokens of a sentence including punctuation.

    >>> tokenize('Bob dropped the apple. Where is the apple?')
    ['Bob', 'dropped', 'the', 'apple', '.', 'Where', 'is', 'the', 'apple', '?']
    '''
    return [x.strip() for x in re.split('(\W+)?', sent) if x.strip()]



>>>>>>> LOCAL
<<<<<<< REMOTE
def tokenize(sent):
    '''Return the tokens of a sentence including punctuation.

    >>> tokenize('Bob dropped the apple. Where is the apple?')
    ['Bob', 'dropped', 'the', 'apple', '.', 'Where', 'is', 'the', 'apple', '?']
    '''
    return [x.strip() for x in re.split('(\W+)?', sent) if x.strip()]



=======
def parse_stories(lines, only_supporting=False):
    '''Parse stories provided in the bAbi tasks format

    If only_supporting is true, only the sentences that support the answer are kept.
    '''
    data = []
    story = []
    for line in lines:
        line = line.decode('utf-8').strip()
        nid, line = line.split(' ', 1)
        nid = int(nid)
        if nid == 1:
            story = []
        if '\t' in line:
            q, a, supporting = line.split('\t')
            q = tokenize(q)
            substory = None
            if only_supporting:
                # Only select the related substory
                supporting = map(int, supporting.split())
                substory = [story[i - 1] for i in supporting]
            else:
                # Provide all the substories
                substory = [x for x in story if x]
            data.append((substory, q, a))
            story.append('')
        else:
            sent = tokenize(line)
            story.append(sent)
    return data



>>>>>>> LOCAL
<<<<<<< REMOTE
def parse_stories(lines, only_supporting=False):
    '''Parse stories provided in the bAbi tasks format

    If only_supporting is true, only the sentences that support the answer are kept.
    '''
    data = []
    story = []
    for line in lines:
        line = line.decode('utf-8').strip()
        nid, line = line.split(' ', 1)
        nid = int(nid)
        if nid == 1:
            story = []
        if '\t' in line:
            q, a, supporting = line.split('\t')
            q = tokenize(q)
            substory = None
            if only_supporting:
                # Only select the related substory
                supporting = map(int, supporting.split())
                substory = [story[i - 1] for i in supporting]
            else:
                # Provide all the substories
                substory = [x for x in story if x]
            data.append((substory, q, a))
            story.append('')
        else:
            sent = tokenize(line)
            story.append(sent)
    return data



=======
def get_stories(f, only_supporting=False, max_length=None):
    '''Given a file name, read the file, retrieve the stories, and then convert the sentences into a single story.

    If max_length is supplied, any stories longer than max_length tokens will be discarded.
    '''
    data = parse_stories(f.readlines(), only_supporting=only_supporting)
    flatten = lambda data: reduce(lambda x, y: x + y, data)
    data = [(flatten(story), q, answer) for story, q, answer in data if not max_length or len(flatten(story)) < max_length]
    return data



>>>>>>> LOCAL
<<<<<<< REMOTE
def get_stories(f, only_supporting=False, max_length=None):
    '''Given a file name, read the file, retrieve the stories, and then convert the sentences into a single story.

    If max_length is supplied, any stories longer than max_length tokens will be discarded.
    '''
    data = parse_stories(f.readlines(), only_supporting=only_supporting)
    flatten = lambda data: reduce(lambda x, y: x + y, data)
    data = [(flatten(story), q, answer) for story, q, answer in data if not max_length or len(flatten(story)) < max_length]
    return data



=======
def vectorize_stories(data, word_idx, story_maxlen, query_maxlen):
    X = []
    Xq = []
    Y = []
    for story, query, answer in data:
        x = [word_idx[w] for w in story]
        xq = [word_idx[w] for w in query]
        y = np.zeros(len(word_idx) + 1)  # let's not forget that index 0 is reserved
        y[word_idx[answer]] = 1
        X.append(x)
        Xq.append(xq)
        Y.append(y)
    return (pad_sequences(X, maxlen=story_maxlen),
            pad_sequences(Xq, maxlen=query_maxlen), np.array(Y))


path = get_file('babi-tasks-v1-2.tar.gz',
                origin='http://www.thespermwhale.com/jaseweston/babi/tasks_1-20_v1-2.tar.gz')
tar = tarfile.open(path)

challenges = {
    # QA1 with 10,000 samples
    'single_supporting_fact_10k': 'tasks_1-20_v1-2/en-10k/qa1_single-supporting-fact_{}.txt',
    # QA2 with 10,000 samples
    'two_supporting_facts_10k': 'tasks_1-20_v1-2/en-10k/qa2_two-supporting-facts_{}.txt',
}
challenge_type = 'single_supporting_fact_10k'
challenge = challenges[challenge_type]

print('Extracting stories for the challenge:', challenge_type)
train_stories = get_stories(tar.extractfile(challenge.format('train')))
test_stories = get_stories(tar.extractfile(challenge.format('test')))

vocab = sorted(reduce(lambda x, y: x | y, (set(story + q + [answer]) for story, q, answer in train_stories + test_stories)))
# Reserve 0 for masking via pad_sequences
vocab_size = len(vocab) + 1
story_maxlen = max(map(len, (x for x, _, _ in train_stories + test_stories)))
query_maxlen = max(map(len, (x for _, x, _ in train_stories + test_stories)))

print('-')
print('Vocab size:', vocab_size, 'unique words')
print('Story max length:', story_maxlen, 'words')
print('Query max length:', query_maxlen, 'words')
print('Number of training stories:', len(train_stories))
print('Number of test stories:', len(test_stories))
print('-')
print('Here\'s what a "story" tuple looks like (input, query, answer):')

>>>>>>> LOCAL
<<<<<<< REMOTE
def vectorize_stories(data, word_idx, story_maxlen, query_maxlen):
    X = []
    Xq = []
    Y = []
    for story, query, answer in data:
        x = [word_idx[w] for w in story]
        xq = [word_idx[w] for w in query]
        y = np.zeros(len(word_idx) + 1)  # let's not forget that index 0 is reserved
        y[word_idx[answer]] = 1
        X.append(x)
        Xq.append(xq)
        Y.append(y)
    return (pad_sequences(X, maxlen=story_maxlen),
            pad_sequences(Xq, maxlen=query_maxlen), np.array(Y))


path = get_file('babi-tasks-v1-2.tar.gz',
                origin='http://www.thespermwhale.com/jaseweston/babi/tasks_1-20_v1-2.tar.gz')
tar = tarfile.open(path)

challenges = {
    # QA1 with 10,000 samples
    'single_supporting_fact_10k': 'tasks_1-20_v1-2/en-10k/qa1_single-supporting-fact_{}.txt',
    # QA2 with 10,000 samples
    'two_supporting_facts_10k': 'tasks_1-20_v1-2/en-10k/qa2_two-supporting-facts_{}.txt',
}
challenge_type = 'single_supporting_fact_10k'
challenge = challenges[challenge_type]

print('Extracting stories for the challenge:', challenge_type)
train_stories = get_stories(tar.extractfile(challenge.format('train')))
test_stories = get_stories(tar.extractfile(challenge.format('test')))

vocab = sorted(reduce(lambda x, y: x | y, (set(story + q + [answer]) for story, q, answer in train_stories + test_stories)))
# Reserve 0 for masking via pad_sequences
vocab_size = len(vocab) + 1
story_maxlen = max(map(len, (x for x, _, _ in train_stories + test_stories)))
query_maxlen = max(map(len, (x for _, x, _ in train_stories + test_stories)))

print('-')
print('Vocab size:', vocab_size, 'unique words')
print('Story max length:', story_maxlen, 'words')
print('Query max length:', query_maxlen, 'words')
print('Number of training stories:', len(train_stories))
print('Number of test stories:', len(test_stories))
print('-')
print('Here\'s what a "story" tuple looks like (input, query, answer):')

=======
print(train_stories[0])
>>>>>>> LOCAL
<<<<<<< REMOTE
print(train_stories[0])
=======
print('-')
>>>>>>> LOCAL
<<<<<<< REMOTE
print('-')
=======
print('Vectorizing the word sequences...')
>>>>>>> LOCAL
<<<<<<< REMOTE
print('Vectorizing the word sequences...')
=======

>>>>>>> LOCAL
<<<<<<< REMOTE

=======
word_idx = dict((c, i + 1) for i, c in enumerate(vocab))
>>>>>>> LOCAL
<<<<<<< REMOTE
word_idx = dict((c, i + 1) for i, c in enumerate(vocab))
=======
inputs_train, queries_train, answers_train = vectorize_stories(train_stories, word_idx, story_maxlen, query_maxlen)
>>>>>>> LOCAL
<<<<<<< REMOTE
inputs_train, queries_train, answers_train = vectorize_stories(train_stories, word_idx, story_maxlen, query_maxlen)
=======
inputs_test, queries_test, answers_test = vectorize_stories(test_stories, word_idx, story_maxlen, query_maxlen)
>>>>>>> LOCAL
<<<<<<< REMOTE
inputs_test, queries_test, answers_test = vectorize_stories(test_stories, word_idx, story_maxlen, query_maxlen)
=======

>>>>>>> LOCAL
<<<<<<< REMOTE

=======
print('-')
>>>>>>> LOCAL
<<<<<<< REMOTE
print('-')
=======
print('inputs: integer tensor of shape (samples, max_length)')
>>>>>>> LOCAL
<<<<<<< REMOTE
print('inputs: integer tensor of shape (samples, max_length)')
=======
print('inputs_train shape:', inputs_train.shape)
>>>>>>> LOCAL
<<<<<<< REMOTE
print('inputs_train shape:', inputs_train.shape)
=======
print('inputs_test shape:', inputs_test.shape)
>>>>>>> LOCAL
<<<<<<< REMOTE
print('inputs_test shape:', inputs_test.shape)
=======
print('-')
>>>>>>> LOCAL
<<<<<<< REMOTE
print('-')
=======
print('queries: integer tensor of shape (samples, max_length)')
>>>>>>> LOCAL
<<<<<<< REMOTE
print('queries: integer tensor of shape (samples, max_length)')
=======
print('queries_train shape:', queries_train.shape)
>>>>>>> LOCAL
<<<<<<< REMOTE
print('queries_train shape:', queries_train.shape)
=======
print('queries_test shape:', queries_test.shape)
>>>>>>> LOCAL
<<<<<<< REMOTE
print('queries_test shape:', queries_test.shape)
=======
print('-')
>>>>>>> LOCAL
<<<<<<< REMOTE
print('-')
=======
print('answers: binary (1 or 0) tensor of shape (samples, vocab_size)')
>>>>>>> LOCAL
<<<<<<< REMOTE
print('answers: binary (1 or 0) tensor of shape (samples, vocab_size)')
=======
print('answers_train shape:', answers_train.shape)
>>>>>>> LOCAL
<<<<<<< REMOTE
print('answers_train shape:', answers_train.shape)
=======
print('answers_test shape:', answers_test.shape)
>>>>>>> LOCAL
<<<<<<< REMOTE
print('answers_test shape:', answers_test.shape)
=======
print('-')
>>>>>>> LOCAL
<<<<<<< REMOTE
print('-')
=======
print('Compiling...')
>>>>>>> LOCAL
<<<<<<< REMOTE
print('Compiling...')
=======

>>>>>>> LOCAL
<<<<<<< REMOTE

=======
# embed the input sequence into a sequence of vectors
>>>>>>> LOCAL
<<<<<<< REMOTE
# embed the input sequence into a sequence of vectors
=======
input_encoder_m = Sequential()
>>>>>>> LOCAL
<<<<<<< REMOTE
input_encoder_m = Sequential()
=======
input_encoder_m.add(Embedding(input_dim=vocab_size,
                              output_dim=64,
                              input_length=story_maxlen))
>>>>>>> LOCAL
<<<<<<< REMOTE
input_encoder_m.add(Embedding(input_dim=vocab_size,
                              output_dim=64,
                              input_length=story_maxlen))
=======
# output: (samples, story_maxlen, embedding_dim)
>>>>>>> LOCAL
<<<<<<< REMOTE
# output: (samples, story_maxlen, embedding_dim)
=======
# embed the question into a single vector
>>>>>>> LOCAL
<<<<<<< REMOTE
# embed the question into a sequence of vectors
=======
question_encoder = Sequential()
>>>>>>> LOCAL
<<<<<<< REMOTE
question_encoder = Sequential()
=======
question_encoder.add(Embedding(input_dim=vocab_size,
                               output_dim=64,
                               input_length=query_maxlen))
>>>>>>> LOCAL
<<<<<<< REMOTE
question_encoder.add(Embedding(input_dim=vocab_size,
                               output_dim=64,
                               input_length=query_maxlen))
=======
# output: (samples, query_maxlen, embedding_dim)
>>>>>>> LOCAL
<<<<<<< REMOTE
# output: (samples, query_maxlen, embedding_dim)
=======
# compute a 'match' between input sequence elements (which are vectors)
>>>>>>> LOCAL
<<<<<<< REMOTE
# compute a 'match' between input sequence elements (which are vectors)
=======
# and the question vector
>>>>>>> LOCAL
<<<<<<< REMOTE
# and the question vector sequence
=======
match = Sequential()
>>>>>>> LOCAL
<<<<<<< REMOTE
match = Sequential()
=======
match.add(Merge([input_encoder_m, question_encoder],
                mode='dot',
                dot_axes=[(2,), (2,)]))
>>>>>>> LOCAL
<<<<<<< REMOTE
match.add(Merge([input_encoder_m, question_encoder],
                mode='dot',
                dot_axes=[(2,), (2,)]))
=======
# output: (samples, story_maxlen, query_maxlen)
>>>>>>> LOCAL
<<<<<<< REMOTE
# output: (samples, story_maxlen, query_maxlen)
=======
# embed the input into a single vector with size = story_maxlen:
>>>>>>> LOCAL
<<<<<<< REMOTE
# embed the input into a single vector with size = story_maxlen:
=======
input_encoder_c = Sequential()
>>>>>>> LOCAL
<<<<<<< REMOTE
input_encoder_c = Sequential()
=======
input_encoder_c.add(Embedding(input_dim=vocab_size,
                              output_dim=query_maxlen,
                              input_length=story_maxlen))
>>>>>>> LOCAL
<<<<<<< REMOTE
input_encoder_c.add(Embedding(input_dim=vocab_size,
                              output_dim=query_maxlen,
                              input_length=story_maxlen))
=======
# output: (samples, story_maxlen, query_maxlen)
>>>>>>> LOCAL
<<<<<<< REMOTE
# output: (samples, story_maxlen, query_maxlen)
=======
# sum the match vector with the input vector:
>>>>>>> LOCAL
<<<<<<< REMOTE
# sum the match vector with the input vector:
=======
response = Sequential()
>>>>>>> LOCAL
<<<<<<< REMOTE
response = Sequential()
=======
response.add(Merge([match, input_encoder_c], mode='sum'))
>>>>>>> LOCAL
<<<<<<< REMOTE
response.add(Merge([match, input_encoder_c], mode='sum'))
=======
# output: (samples, story_maxlen, query_maxlen)
>>>>>>> LOCAL
<<<<<<< REMOTE
# output: (samples, story_maxlen, query_maxlen)
=======
response.add(Permute((2, 1)))  # output: (samples, query_maxlen, story_maxlen)
>>>>>>> LOCAL
<<<<<<< REMOTE
response.add(Permute((2, 1)))  # output: (samples, query_maxlen, story_maxlen)
=======

>>>>>>> LOCAL
<<<<<<< REMOTE

=======
# concatenate the match vector with the question vector,
>>>>>>> LOCAL
<<<<<<< REMOTE
# concatenate the match vector with the question vector,
=======
# and do logistic regression on top
>>>>>>> LOCAL
<<<<<<< REMOTE
# and do logistic regression on top
=======
answer = Sequential()
>>>>>>> LOCAL
<<<<<<< REMOTE
answer = Sequential()
=======
answer.add(Merge([response, question_encoder], mode='concat', concat_axis=-1))
>>>>>>> LOCAL
<<<<<<< REMOTE
answer.add(Merge([response, question_encoder], mode='concat', concat_axis=-1))
=======
# the original paper uses a matrix multiplication for this reduction step.
>>>>>>> LOCAL
<<<<<<< REMOTE
# the original paper uses a matrix multiplication for this reduction step.
=======
# we choose to use a RNN instead.
>>>>>>> LOCAL
<<<<<<< REMOTE
# we choose to use a RNN instead.
=======
answer.add(LSTM(64))
>>>>>>> LOCAL
<<<<<<< REMOTE
answer.add(LSTM(64))
=======
# one regularization layer -- more would probably be needed.
>>>>>>> LOCAL
<<<<<<< REMOTE
# one regularization layer -- more would probably be needed.
=======
answer.add(Dropout(0.25))
>>>>>>> LOCAL
<<<<<<< REMOTE
answer.add(Dropout(0.25))
=======
answer.add(Dense(vocab_size))
>>>>>>> LOCAL
<<<<<<< REMOTE
answer.add(Dense(vocab_size))
=======
# we output a probability distribution over the vocabulary
>>>>>>> LOCAL
<<<<<<< REMOTE
# we output a probability distribution over the vocabulary
=======
answer.add(Activation('softmax'))
>>>>>>> LOCAL
<<<<<<< REMOTE
answer.add(Activation('softmax'))
=======

>>>>>>> LOCAL
<<<<<<< REMOTE

=======
answer.compile(optimizer='rmsprop', loss='categorical_crossentropy')
>>>>>>> LOCAL
<<<<<<< REMOTE
answer.compile(optimizer='rmsprop', loss='categorical_crossentropy')
=======
# Note: you could use a Graph model to avoid repeat the input twice
>>>>>>> LOCAL
<<<<<<< REMOTE
# Note: you could use a Graph model to avoid repeat the input twice
=======
answer.fit([inputs_train, queries_train, inputs_train], answers_train,
           batch_size=32,
           nb_epoch=70,
           show_accuracy=True,
           validation_data=([inputs_test, queries_test, inputs_test], answers_test))
>>>>>>> LOCAL
answer.fit([inputs_train, queries_train, inputs_train], answers_train,
           batch_size=32,
           nb_epoch=70,
           show_accuracy=True,
           validation_data=([inputs_test, queries_test, inputs_test], answers_test))

