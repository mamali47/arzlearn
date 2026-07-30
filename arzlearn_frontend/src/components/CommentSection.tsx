import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { deleteComment, fetchComments, postComment, updateComment } from '../api/endpoints'
import { useAuth } from '../context/AuthContext'
import type { CommentItem } from '../api/types'
import { formatDatePersian, parseApiErrors } from '../utils/apiError'
import './CommentSection.css'

interface CommentRowProps {
  comment: CommentItem
  onUpdated: (updated: CommentItem) => void
  onDeleted: (id: number) => void
}

function CommentRow({ comment, onUpdated, onDeleted }: CommentRowProps) {
  const [isEditing, setIsEditing] = useState(false)
  const [draft, setDraft] = useState(comment.body)
  const [saving, setSaving] = useState(false)
  const [deleting, setDeleting] = useState(false)
  const [rowError, setRowError] = useState<string | null>(null)

  async function handleSave() {
    if (!draft.trim()) return
    setSaving(true)
    setRowError(null)
    try {
      const updated = await updateComment(comment.id, draft.trim())
      onUpdated(updated)
      setIsEditing(false)
    } catch (err) {
      setRowError(parseApiErrors(err).general ?? 'ویرایش دیدگاه با خطا مواجه شد.')
    } finally {
      setSaving(false)
    }
  }

  async function handleDelete() {
    if (!window.confirm('آیا از حذف این دیدگاه مطمئن هستید؟')) return
    setDeleting(true)
    setRowError(null)
    try {
      await deleteComment(comment.id)
      onDeleted(comment.id)
    } catch (err) {
      setRowError(parseApiErrors(err).general ?? 'حذف دیدگاه با خطا مواجه شد.')
      setDeleting(false)
    }
  }

  return (
    <li className="comment-item">
      <div className="comment-avatar">
        {comment.avatar ? (
          <img src={comment.avatar} alt={comment.display_name} />
        ) : (
          <span>{comment.display_name.charAt(0).toUpperCase()}</span>
        )}
      </div>
      <div className="comment-body">
        <div className="comment-meta">
          <span className="comment-username">{comment.display_name}</span>
          <span className="text-muted">{formatDatePersian(comment.created_at)}</span>
        </div>

        {isEditing ? (
          <div className="comment-edit-form">
            <textarea value={draft} onChange={(e) => setDraft(e.target.value)} rows={3} maxLength={1000} />
            {rowError && <p className="field-error">{rowError}</p>}
            <div className="comment-edit-actions">
              <button className="btn btn-primary" onClick={handleSave} disabled={saving}>
                {saving ? 'در حال ذخیره...' : 'ذخیره'}
              </button>
              <button
                className="btn btn-outline"
                onClick={() => {
                  setIsEditing(false)
                  setDraft(comment.body)
                  setRowError(null)
                }}
                disabled={saving}
              >
                انصراف
              </button>
            </div>
          </div>
        ) : (
          <>
            <p>{comment.body}</p>
            {comment.is_owner && (
              <div className="comment-owner-actions">
                <button className="comment-action-btn" onClick={() => setIsEditing(true)}>
                  ویرایش
                </button>
                <button className="comment-action-btn danger" onClick={handleDelete} disabled={deleting}>
                  {deleting ? 'در حال حذف...' : 'حذف'}
                </button>
              </div>
            )}
            {rowError && <p className="field-error">{rowError}</p>}
          </>
        )}
      </div>
    </li>
  )
}

export default function CommentSection({ articleId, articleSlug }: { articleId: number; articleSlug: string }) {
  const [comments, setComments] = useState<CommentItem[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [body, setBody] = useState('')
  const [error, setError] = useState<string | null>(null)
  const [submitting, setSubmitting] = useState(false)
  const { user } = useAuth()

  useEffect(() => {
    setIsLoading(true)
    fetchComments(articleSlug)
      .then(setComments)
      .catch(() => setComments([]))
      .finally(() => setIsLoading(false))
  }, [articleSlug])

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault()
    if (!body.trim()) return
    setSubmitting(true)
    setError(null)
    try {
      const newComment = await postComment({ article: articleId, body: body.trim() })
      setComments((prev) => [newComment, ...prev])
      setBody('')
    } catch (err) {
      setError(parseApiErrors(err).general ?? 'ثبت دیدگاه با خطا مواجه شد.')
    } finally {
      setSubmitting(false)
    }
  }

  function handleUpdated(updated: CommentItem) {
    setComments((prev) => prev.map((c) => (c.id === updated.id ? updated : c)))
  }

  function handleDeleted(id: number) {
    setComments((prev) => prev.filter((c) => c.id !== id))
  }

  return (
    <section className="comment-section card">
      <h3 className="section-title">دیدگاه‌ها ({comments.length})</h3>

      {user ? (
        <form className="comment-form" onSubmit={handleSubmit}>
          <textarea
            placeholder="نظر خود را بنویسید..."
            value={body}
            onChange={(e) => setBody(e.target.value)}
            rows={3}
            maxLength={1000}
          />
          {error && <p className="field-error">{error}</p>}
          <button type="submit" className="btn btn-primary" disabled={submitting}>
            {submitting ? 'در حال ارسال...' : 'ارسال نظر'}
          </button>
        </form>
      ) : (
        <p className="comment-login-prompt text-muted">
          برای ثبت دیدگاه ابتدا <Link to="/login">وارد حساب کاربری</Link> خود شوید.
        </p>
      )}

      {isLoading ? (
        <p className="text-muted">در حال بارگذاری دیدگاه‌ها...</p>
      ) : comments.length === 0 ? (
        <p className="text-muted">هنوز دیدگاهی ثبت نشده است. اولین نفر باشید!</p>
      ) : (
        <ul className="comment-list">
          {comments.map((comment) => (
            <CommentRow key={comment.id} comment={comment} onUpdated={handleUpdated} onDeleted={handleDeleted} />
          ))}
        </ul>
      )}
    </section>
  )
}
