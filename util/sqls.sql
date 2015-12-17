#동시에 팔로잉 하고있는 계정의 리스트 받기
SELECT 
    twitter.relationship.follower
FROM
    twitter.relationship
WHERE
    twitter.relationship.follower in 
    (select twitter.relationship.follower from twitter.relationship
    where twitter.relationship.following = 281916923)
    and twitter.relationship.following = 335204566;

#팔로잉 타겟의 계정명을 검색
SELECT DISTINCT
    (twitter.relationship.following) as foo, 
    twitter.user.screen_name
FROM
    twitter.relationship,
    twitter.user
WHERE
    twitter.relationship.following = twitter.user.id;

#335204566을 팔로잉하는 유저들의 트윗 검색
SELECT 
    *
FROM
    tweet
WHERE
    tweet.user IN (SELECT 
            relationship.follower
        FROM
            relationship
        WHERE
            following = 335204566);

#tweet_335204566_1에 335204566을 팔로잉하는 유저들의 트윗을 0번째 트윗부터 1000000개 삽입
insert into tweet_335204566_1 SELECT 
    *
FROM
    tweet
WHERE
    tweet.user IN (SELECT 
            relationship.follower
        FROM
            relationship
        WHERE
            following = 335204566)
LIMIT 0, 1000000;

#tweet_335204566_4에 335204566을 팔로잉하는 유저들의 트윗을 id가 275429499905118208보다 큰 id의 트윗부터 1000000개 삽입
insert into tweet_335204566_4 SELECT 
    *
FROM
    tweet
WHERE
    tweet.user IN (SELECT 
            relationship.follower
        FROM
            relationship
        WHERE
            following = 335204566) and
tweet.id > 275429499905118208 LIMIT 1000000;

#word_analysis_log로 부터 word_count내림차순으로 corpus에 없는 단어들만 출력
SELECT 
    word_analysis_log.search_log_type,
    word_analysis_log.word_count,
    word_table.word,
    word_table.pos
FROM
    twitter.word_analysis_log,
    twitter.word_table
WHERE
    word_analysis_log.word_id = word_table.id
    and word_table.unknown = 1
    #and word_table.pos="Noun"
ORDER BY word_count DESC;

#281916923을 following하고 있으면서 아직 트윗이 수집되지 않은 user의 수를 표시
SELECT 
    count(id)
FROM
    twitter.user
WHERE
    user.id IN (SELECT 
            relationship.follower
        FROM
            relationship
        WHERE
            relationship.following = 281916923)
    and user.tweet_collected_date is NULL;
