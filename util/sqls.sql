#max, min 찾기
SELECT 
    MAX(id), MAX(created_at), MIN(id), MIN(created_at)
FROM
    tweet_44771983_1;
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
#tweet_search_log로부터 tweet_id가 중복되서 등장하는 리스트를 보여줌
SELECT
    tweet_id, COUNT(*)
FROM
    tweet_search_log
GROUP BY
    tweet_id
HAVING 
    COUNT(*) > 1

#tweet_search_log중 text에 'https'가 포함되어 있고 검색한 tweet_type이 9인 트윗들 가져오기
SELECT 
    *
FROM
    tweet_335204566_9 AS t
WHERE
    t.id IN (SELECT 
            tweet_id
        FROM
            tweet_search_log
        WHERE
            tweet_type = 9 AND t.text LIKE '%https%');

#search_log_type=9인 word analysis log와 search_logt_type=10인 word analysis log의 교집합 중에 search_log_type이 10인 word들의 집합.
SELECT 
    word_analysis_log.search_log_type,
    word_analysis_log.word_id,
    word_analysis_log.word_count,
    word_table.word,
    word_table.pos
FROM
    twitter.word_analysis_log,
    twitter.word_table
WHERE
    word_analysis_log.word_id = word_table.id
        AND word_analysis_log.word_id IN (SELECT 
            word_id
        FROM
            word_analysis_log
        WHERE
            search_log_type = 9)
        AND word_analysis_log.word_id IN (SELECT 
            word_id
        FROM
            word_analysis_log
        WHERE
            search_log_type = 10)
        AND (search_log_type = 10)
GROUP BY word
ORDER BY word_count DESC;

#search_log_type=9이면서 search_log_type=10에 나타나지 않은 단어들을 대상으로 screen_name을 제외한 단어들을 나타낸 것
#별로 의미있는 정보를 도출하지는 못하는듯..
SELECT 
    word_analysis_log.search_log_type,
    word_analysis_log.word_id,
    word_analysis_log.word_count,
    word_table.word,
    word_table.pos
FROM
    twitter.word_analysis_log,
    twitter.word_table
WHERE
    word_analysis_log.word_id = word_table.id
        AND word_analysis_log.word_id IN (SELECT 
            word_id
        FROM
            word_analysis_log
        WHERE
            search_log_type = 9)
        AND word_analysis_log.word_id NOT IN (SELECT 
            word_id
        FROM
            word_analysis_log
        WHERE
            search_log_type = 10)
        AND search_log_type = 9
        AND pos != 'ScreenName'
GROUP BY word
ORDER BY word_count DESC;

#모든 tweet horizontal partitions에 대한 id count를 반환
#TODO : tweet horizontal partitions 테이블 이름 값을 특정 테이블에 저장하도록 해야할듯.
SELECT 
    (SELECT 
            COUNT(id)
        FROM
            tweet_281916923_1) + (SELECT 
            COUNT(id)
        FROM
            tweet_335204566_1) + (SELECT 
            COUNT(id)
        FROM
            tweet_335204566_2) + (SELECT 
            COUNT(id)
        FROM
            tweet_335204566_3) + (SELECT 
            COUNT(id)
        FROM
            tweet_335204566_4) + (SELECT 
            COUNT(id)
        FROM
            tweet_335204566_5) + (SELECT 
            COUNT(id)
        FROM
            tweet_335204566_6) + (SELECT 
            COUNT(id)
        FROM
            tweet_335204566_7) + (SELECT 
            COUNT(id)
        FROM
            tweet_335204566_8) + (SELECT 
            COUNT(id)
        FROM
            tweet_335204566_9) AS sum;

#특정 word가 word_analysis에서 어디에 등장했는지에 대해서
SELECT 
    word_analysis_log.word_count,
    word_analysis_log.word_id AS id,
    word_analysis_log.search_log_type AS tweet_type,
    word_table.word AS word,
    word_table.pos AS pos,
    word_table.unknown,
    word_table.created_at AS word_created_at,
    word_analysis_log.created_at AS word_analyzed_at
FROM
    word_analysis_log
        JOIN
    word_table ON word_analysis_log.word_id = word_table.id
WHERE
    word_id IN (SELECT 
            id
        FROM
            word_table
        WHERE
            word_table.word = '은');

#tweet_search_log로부터 tweet을 불러오는 sql
#TODO : 여러 가지의 partition으로부터 text를 불러올 수 있게 해야함
SELECT 
    *
FROM
    tweet_335204566_9
WHERE
    tweet_335204566_9.id IN (SELECT 
            tweet_id
        FROM
            twitter.tweet_search_log
        WHERE
            tweet_type = 18);


# Drop Alter
# http://stackoverflow.com/questions/7599519/alter-table-add-column-takes-a-long-time
CREATE TABLE user_new LIKE user;
ALTER TABLE user_new 
ADD COLUMN `updated_date` DATETIME NULL COMMENT '' AFTER `created_date`;
INSERT INTO user_new (id, screen_name, statuses_count, name, follower_count, tweet_collected_date, created_date,language_type,
authorized,protected) SELECT * FROM user;
RENAME TABLE user TO user_old, user_new TO user;

# Get latest 30 tweets per user in estimated_bot_user_list and tweet_search_log
set @num := 0, @user := '';

SELECT 
    *
FROM
    (SELECT 
        tweet_1364028594_2.*,
            @num:=IF(@user = tweet_1364028594_2.user, @num + 1, 1) AS row_number,
            @user:=tweet_1364028594_2.user AS dummy
    FROM
        tweet_1364028594_2
    WHERE
        user IN (SELECT 
                user_id
            FROM
                estimated_bot_user_list
            WHERE
                type_id = 8)
            AND id IN (SELECT 
                tweet_id
            FROM
                tweet_search_log
            WHERE
                tweet_type = 8)
    ORDER BY user, id desc) AS x
WHERE
    x.row_number <= 30;

# Word Analysis Without bot account 테이블에서 특정 트윗타입의 단어를 카운트 역순으로 가져옴
SELECT
    word_analysis_log.search_log_type,
    word_analysis_log.word_id,
    word_analysis_log.word_count,
    word_table.word,
    word_table.pos
FROM
    twitter.word_analysis_log,
    twitter.word_table
WHERE
    word_analysis_log.word_id = word_table.id
        AND word_analysis_log.word_id IN (SELECT
            word_id
        FROM
            word_analysis_log
        WHERE
            search_log_type = 8)
    and word_analysis_log.search_log_type = 8
    and (word_table.pos = "Noun" or word_table.pos="Hashtag")
GROUP BY word_table.word
ORDER BY word_count DESC;

#두개 word_analysis 테이블로부터 word_id별로 count를 비교하기 위한 쿼리 (used inner join)
SELECT
    #word_analysis_log.word_id,
    t2.word_count as before_c
    ,t1.word_count as filtered_c
    ,(t1.word_count / t2.word_count) as ratio
    ,word_table.word as word
    #,word_table.pos
FROM
    twitter.w_analysis_without_bot as t1 left outer join 
    twitter.word_analysis_log as t2 on t1.word_id=t2.word_id,
    twitter.word_table
WHERE
    t1.word_id = word_table.id
        AND t1.word_id IN (SELECT
            word_id
        FROM
            word_analysis_log
        WHERE
            search_log_type = 8)
    and t1.search_log_type = 8
    and (word_table.pos="Hashtag")
GROUP BY word_table.word
ORDER BY t2.word_count DESC
