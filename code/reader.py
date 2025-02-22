import codecs
import re
import operator

num_regex = re.compile('^[+-]?[0-9]+\.?[0-9]*$')

def is_number(token):
    return bool(num_regex.match(token))

#max_len:최대 길이를 제한하기 위한 값, vocab_size : 단어 사전의 크기를 제한하기 위한 값
#maxlen보다 긴 문장은 제외하고 단어별 빈도수 세어, 빈도수가 높은 단어부터 정렬해 vocab 사전 생성
def create_vocab(domain, maxlen=0, vocab_size=0):
    assert domain in {'food'}
    source = '../preprocessed_data/'+domain+'/train.txt'

    total_words, unique_words = 0, 0
    word_freqs = {}
    top = 0

    
    fin = codecs.open(source, 'r', 'utf-8')
    for line in fin:
        words = line.split()
        if maxlen > 0 and len(words) > maxlen:
            continue

        for w in words:
            if not is_number(w):
                try:
                    word_freqs[w] += 1
                except KeyError:
                    unique_words += 1
                    word_freqs[w] = 1
                total_words += 1

    print ('   %i total words, %i unique words' % (total_words, unique_words))
    sorted_word_freqs = sorted(word_freqs.items(), key=operator.itemgetter(1), reverse=True)

    vocab = {'<pad>':0, '<unk>':1, '<num>':2}
    index = len(vocab)
    for word, _ in sorted_word_freqs:
        vocab[word] = index
        index += 1
        if vocab_size > 0 and index > vocab_size + 2:
            break
    if vocab_size > 0:
        print ('  keep the top %i words' % vocab_size)

    #Write (vocab, frequence) to a txt file
    vocab_file = codecs.open('../preprocessed_data/%s/vocab' % domain, mode='w', encoding='utf8')
    sorted_vocab = sorted(vocab.items(), key=operator.itemgetter(1))
    for word, index in sorted_vocab:
        if index < 3:
            vocab_file.write(word+'\t'+str(0)+'\n')
            continue
        vocab_file.write(word+'\t'+str(word_freqs[word])+'\n')
    vocab_file.close()

    return vocab


#maxlen값보다 긴 문장은 제외하고 vocab 사전에 있는 단어는 해당하는 index로 
#숫자는 <num>, vocab에 없는 단어는 <unk>로 대체한 후 이를 리스트로 저장.  

def read_dataset(domain, phase, vocab, maxlen):
    assert domain in {'food'}#'restaurant', 'beer'
    assert phase in {'train', 'test'}
    
    source = '../preprocessed_data/'+domain+'/'+phase+'.txt'
    num_hit, unk_hit, total = 0., 0., 0.
    maxlen_x = 0
    data_x = []
    
    fin = codecs.open(source, 'r', 'utf-8')
    for line in fin:
        words = line.strip().split()
        if maxlen > 0 and len(words) > maxlen:
            continue

        indices = []
        for word in words:
            if is_number(word):
                indices.append(vocab['<num>'])
                num_hit += 1
            elif word in vocab:
                indices.append(vocab[word])
            else:
                indices.append(vocab['<unk>'])
                unk_hit += 1
            total += 1

        data_x.append(indices)
        if maxlen_x < len(indices):
            maxlen_x = len(indices)

    print ('   <num> hit rate: %.2f%%, <unk> hit rate: %.2f%%' % (100*num_hit/total, 100*unk_hit/total))
    return data_x, maxlen_x

#create_vocab과 read_dataset 함수를 호출해 vocab 사전과 train/test 데이터셋을 생성. 
#vocab,train_x,test_x,maxlen 값을 반환
def get_data(domain, vocab_size=0, maxlen=0):
    print( 'Reading data from', domain)
    print( ' Creating vocab ...')
    vocab = create_vocab(domain, maxlen, vocab_size)
    print( ' Reading dataset ...')
    print('  train set') 
    train_x, train_maxlen = read_dataset(domain, 'train', vocab, maxlen)
    print('  test set') 
    test_x, test_maxlen = read_dataset(domain, 'test', vocab, maxlen)
    maxlen = max(train_maxlen, test_maxlen)
    return vocab, train_x, test_x, maxlen
    


if __name__ == "__main__":
    vocab, train_x, test_x, maxlen = get_data('food')#reataurant 여기 도메인에 맞게 바꾸기
    print(len(train_x)) 
    print(len(test_x)) 
    print(maxlen) 

"""
텍스트 데이터를 전처리하고 해당 데이터셋에 대한 단어 사전을 생성하면 학습 및 테스트 데이터셋을 생성하는 기능 수행
"""