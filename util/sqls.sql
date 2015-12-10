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
