package com.example.application.repository;

import com.example.application.entity.Book;
import com.example.application.entity.ChatHistory;
import com.example.application.type.Sender;
import com.example.application.type.ChatState;
import com.example.application.entity.User;
import jakarta.transaction.Transactional;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Modifying;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.util.List;
import java.util.Optional;

public interface ChatHistoryRepository extends JpaRepository<ChatHistory, Long> {

    /**
     * [N+1 해결: 페치 조인(Fetch Join)]
     * 특정 사용자와 책의 모든 채팅 기록을 조회함.
     * * [이유]
     * 이 메소드가 반환한 List<ChatHistory>를 컨트롤러/뷰에서 사용할 때,
     * 'ch.user.name'이나 'ch.book.title'처럼 LAZY 필드에 접근하면 N+1 쿼리가 발생함.
     * 'JOIN FETCH'는 연관된 User와 Book을 즉시 함께 로드(Eager Loading)하여
     * N+1 문제를 원천 방지함.
     *
     * @param user 조회할 User 엔티티 (프록시)
     * @param book 조회할 Book 엔티티 (프록시)
     * @return User와 Book이 페치 조인된 ChatHistory 목록 (시간순)
     */
    @Query("SELECT ch FROM ChatHistory ch " +
            "JOIN FETCH ch.user u " +
            "JOIN FETCH ch.book b " +
            "WHERE ch.user = :user AND ch.book = :book " +
            "ORDER BY ch.createdAt ASC")
    List<ChatHistory> findAllByUserAndBookOrderByCreatedAtAsc(@Param("user") User user, @Param("book") Book book);

    /**
     * 특정 사용자와 책의 '가장 마지막' 채팅 기록 1건을 조회함.
     * (단일 건(Top 1) 조회는 N+1을 유발하지 않으므로 페치 조인 불필요.)
     *
     * @param user 조회할 User 엔티티
     * @param book 조회할 Book 엔티티
     * @return 가장 마지막 ChatHistory (Optional)
     */
    Optional<ChatHistory> findTopByUserAndBookOrderByCreatedAtDesc(User user, Book book);

    /**
     * 특정 사용자와 책, 발신자(Sender) 기준 '가장 마지막' 채팅 기록 1건을 조회함.
     * (예: 가장 마지막 USER의 답변 조회)
     *
     * @param user User 엔티티
     * @param book Book 엔티티
     * @param sender 발신자 (AI or USER)
     * @return 가장 마지막 ChatHistory (Optional)
     */
    Optional<ChatHistory> findTopByUserAndBookAndSenderOrderByCreatedAtDesc(User user, Book book, Sender sender);

    /**
     * [성능 최적화: 일괄 삭제(Bulk Delete)]
     * 특정 사용자와 책에 해당하는 모든 채팅 기록을 일괄 삭제함.
     * @Modifying과 @Query를 사용하여 영속성 컨텍스트를 거치지 않고 DB로 DELETE 쿼리를 직접 실행.
     *
     * @param user 삭제할 User 엔티티
     * @param book 삭제할 Book 엔티티
     */
    @Transactional
    @Modifying
    @Query("DELETE FROM ChatHistory ch WHERE ch.user = :user AND ch.book = :book")
    void deleteAllByUserAndBook(@Param("user") User user, @Param("book") Book book);

    /**
     * [성능 최적화: DB 필터링]
     * 'ChatService'에서 AI 설명 컨텍스트를 구성하기 위해,
     * '설명(PRESENTING_CONCEPT_EXPLANATION)'과 '평가(WAITING_CONCEPT_RATING)' 상태의
     * 채팅 기록 목록만 DB에서 직접 필터링하여 조회.
     * (불필요한 전체 채팅 이력을 조회하지 않도록 최적화)
     *
     * @param user User 엔티티
     * @param book Book 엔티티
     * @param sender 발신자 (AI)
     * @param states 조회할 ChatState 목록 (IN 절)
     * @return 필터링된 ChatHistory 목록 (최신순)
     */
    @Query("SELECT ch FROM ChatHistory ch WHERE ch.user = :user AND ch.book = :book AND ch.sender = :sender " +
            "AND ch.chatState IN (:states) ORDER BY ch.createdAt DESC")
    List<ChatHistory> findAiExplanationsWithRatingsByUserAndBookAndStates(
            @Param("user") User user,
            @Param("book") Book book,
            @Param("sender") Sender sender,
            @Param("states") List<ChatState> states
    );

    /**
     * [N+1 문제 해결: 반복문 내 쿼리 방지]
     * 'ChatService'에서 '낮은 점수 사유(피드백)'를 찾기 위해 반복문 내에서 개별 쿼리를 호출하는
     * N+1 문제를 해결하기 위해, 모든 피드백('WAITING_REASON_FOR_LOW_RATING')을
     * '미리' 한 번에 조회함. (In-Memory Join용)
     *
     * @param user User 엔티티
     * @param book Book 엔티티
     * @param sender 발신자 (USER)
     * @param state 조회할 ChatState (WAITING_REASON_FOR_LOW_RATING)
     * @return 피드백 ChatHistory 목록 (시간순)
     */
    @Query("SELECT ch FROM ChatHistory ch " +
            "WHERE ch.user = :user AND ch.book = :book " +
            "AND ch.sender = :sender AND ch.chatState = :state " +
            "ORDER BY ch.createdAt ASC")
    List<ChatHistory> findAllFeedbacks(
            @Param("user") User user,
            @Param("book") Book book,
            @Param("sender") Sender sender,
            @Param("state") ChatState state
    );
}