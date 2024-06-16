'use client'

import { usePathname } from 'next/navigation'

export const Navigation = () => {
  const pathName = usePathname()

  return (
    <nav
      id='nav'
      className='absolute left-0 right-0 top-8 z-[51] container flex items-center max-w-6xl mx-auto space-x-5 w-full text-sm text-gray-800'
    >
      <a
        href='/'
        className={`font-bold duration-100 transition-color hover:text-indigo-600 ${
          pathName === '/' ? 'text-indigo-600' : ''
        }`}
      >
        Проверить
      </a>
      <a
        href='/admin'
        className={`font-bold duration-100 transition-color hover:text-indigo-600 ${
          pathName === '/admin' ? 'text-indigo-600' : ''
        }`}
      >
        Загрузить оригинал (админ)
      </a>
    </nav>
  )
}
