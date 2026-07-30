import { useState } from 'react'
import type { ArticleFAQ } from '../api/types'
import './ArticleFAQSection.css'

function FAQItem({ faq }: { faq: ArticleFAQ }) {
  const [isOpen, setIsOpen] = useState(false)

  return (
    <div className={`faq-item ${isOpen ? 'faq-item--open' : ''}`}>
      <button className="faq-item__question" onClick={() => setIsOpen((v) => !v)}>
        <span>{faq.question}</span>
        <svg
          className="faq-item__chevron"
          width="18"
          height="18"
          viewBox="0 0 24 24"
          fill="none"
        >
          <path
            d="M6 9l6 6 6-6"
            stroke="currentColor"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
      </button>
      {isOpen && <div className="faq-item__answer">{faq.answer}</div>}
    </div>
  )
}

export default function ArticleFAQSection({ faqs }: { faqs: ArticleFAQ[] }) {
  if (faqs.length === 0) return null

  return (
    <section className="article-faq-section card">
      <h2 className="section-title">سوالات متداول</h2>
      <div className="article-faq-section__list">
        {faqs.map((faq) => (
          <FAQItem key={faq.id} faq={faq} />
        ))}
      </div>
    </section>
  )
}
