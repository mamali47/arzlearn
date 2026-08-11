import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { fetchSocialLinks } from '../api/endpoints'
import type { SocialLink } from '../api/types'
import './Footer.css'

export default function Footer() {
  const [socials, setSocials] = useState<SocialLink[]>([])

  useEffect(() => {
    fetchSocialLinks()
      .then(setSocials)
      .catch(() => setSocials([]))
  }, [])

  return (
    <footer className="site-footer">
      <div className="container footer-inner">
        <div className="container footer-about">
        <p>
          ارزلرن یک مجله تخصصی بازارهای مالی است که جدیدترین اخبار ارزهای دیجیتال،
          آموزش‌های کاربردی، تحلیل بازار، بررسی صرافی‌ها و بروکرها، همچنین قیمت
          لحظه‌ای ارز، دلار و طلا را ارائه می‌دهد. هدف ما ارائه اطلاعات دقیق و کاربردی
          برای علاقه‌مندان به بازارهای مالی است.
        </p>
      </div>
        <div className="footer-brand">
          <Link to="/" className="site-logo">
            <img src="/logo.png" alt="ارزلرن" className="site-logo__image" />
            <span>ارزلرن</span>
          </Link>
          <p className="text-muted">
            مرجع اخبار، تحلیل و قیمت لحظه‌ای ارزهای دیجیتال و طلا.
          </p>
          <Link to="/about" className="footer-about-link">
            درباره ما
          </Link>
        </div>

        <div className="footer-socials">
          <h4>ارزلرن در شبکه‌های اجتماعی</h4>
          <ul>
            {socials.map((social) => (
              <li key={social.id}>
                <a href={social.url} target="_blank" rel="noopener noreferrer">
                  {social.icon && <img src={social.icon} alt={social.platform_name} />}
                  <span>{social.platform_name}</span>
                </a>
              </li>
            ))}
          </ul>
        </div>

        <div className="footer-contact">
          <h4>تماس با ما</h4>
          <a href="mailto:ir.arzlearn@gmail.com" className="footer-contact__email">
            ir.arzlearn@gmail.com
          </a>
        </div>
      </div>

      <div className="footer-bottom">
        <p>© {new Date().getFullYear()} ارزلرن. تمامی حقوق محفوظ است.</p>
      </div>
    </footer>
  )
}
