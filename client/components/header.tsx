export const Header = () => {
  return (
    <header className='relative z-50 w-full h-24'>
      <div className='container flex items-center justify-center h-full max-w-6xl px-8 mx-auto sm:justify-between xl:px-0'>
        <div className='absolute right-0 flex-col items-center justify-center w-full pb-8 mt-48 border-gray-200 '>
          <svg
            className='absolute top-0 right-0 hidden w-screen max-w-3xl -mt-64 -ml-12 lg:block'
            viewBox='0 0 818 815'
            xmlns='http://www.w3.org/2000/svg'
            xmlnsXlink='http://www.w3.org/1999/xlink'
          >
            <defs>
              <linearGradient
                x1='0%'
                y1='0%'
                x2='100%'
                y2='100%'
                id='c'
              >
                <stop
                  stopColor='#E614F2'
                  offset='0%'
                />
                <stop
                  stopColor='#FC3832'
                  offset='100%'
                />
              </linearGradient>
              <linearGradient
                x1='0%'
                y1='0%'
                x2='100%'
                y2='100%'
                id='f'
              >
                <stop
                  stopColor='#657DE9'
                  offset='0%'
                />
                <stop
                  stopColor='#1C0FD7'
                  offset='100%'
                />
              </linearGradient>
              <filter
                x='-4.7%'
                y='-3.3%'
                width='109.3%'
                height='109.3%'
                filterUnits='objectBoundingBox'
                id='a'
              >
                <feOffset
                  dy='8'
                  in='SourceAlpha'
                  result='shadowOffsetOuter1'
                />
                <feGaussianBlur
                  stdDeviation='8'
                  in='shadowOffsetOuter1'
                  result='shadowBlurOuter1'
                />
                <feColorMatrix
                  values='0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.15 0'
                  in='shadowBlurOuter1'
                />
              </filter>
              <filter
                x='-4.7%'
                y='-3.3%'
                width='109.3%'
                height='109.3%'
                filterUnits='objectBoundingBox'
                id='d'
              >
                <feOffset
                  dy='8'
                  in='SourceAlpha'
                  result='shadowOffsetOuter1'
                />
                <feGaussianBlur
                  stdDeviation='8'
                  in='shadowOffsetOuter1'
                  result='shadowBlurOuter1'
                />
                <feColorMatrix
                  values='0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0.2 0'
                  in='shadowBlurOuter1'
                />
              </filter>
              <path
                d='M160.52 108.243h497.445c17.83 0 24.296 1.856 30.814 5.342 6.519 3.486 11.635 8.602 15.12 15.12 3.487 6.52 5.344 12.985 5.344 30.815v497.445c0 17.83-1.857 24.296-5.343 30.814-3.486 6.519-8.602 11.635-15.12 15.12-6.52 3.487-12.985 5.344-30.815 5.344H160.52c-17.83 0-24.296-1.857-30.814-5.343-6.519-3.486-11.635-8.602-15.12-15.12-3.487-6.52-5.343-12.985-5.343-30.815V159.52c0-17.83 1.856-24.296 5.342-30.814 3.486-6.519 8.602-11.635 15.12-15.12 6.52-3.487 12.985-5.343 30.815-5.343z'
                id='b'
              />
              <path
                d='M159.107 107.829H656.55c17.83 0 24.296 1.856 30.815 5.342 6.518 3.487 11.634 8.602 15.12 15.12 3.486 6.52 5.343 12.985 5.343 30.816V656.55c0 17.83-1.857 24.296-5.343 30.815-3.486 6.518-8.602 11.634-15.12 15.12-6.519 3.486-12.985 5.343-30.815 5.343H159.107c-17.83 0-24.297-1.857-30.815-5.343-6.519-3.486-11.634-8.602-15.12-15.12-3.487-6.519-5.343-12.985-5.343-30.815V159.107c0-17.83 1.856-24.297 5.342-30.815 3.487-6.519 8.602-11.634 15.12-15.12 6.52-3.487 12.985-5.343 30.816-5.343z'
                id='e'
              />
            </defs>
            <g
              fill='none'
              fillRule='evenodd'
              opacity='.9'
            >
              <g transform='rotate(65 416.452 409.167)'>
                <use
                  fill='#000'
                  filter='url(#a)'
                  xlinkHref='#b'
                />
                <use
                  fill='url(#c)'
                  xlinkHref='#b'
                />
              </g>
              <g transform='rotate(29 421.929 414.496)'>
                <use
                  fill='#000'
                  filter='url(#d)'
                  xlinkHref='#e'
                />
                <use
                  fill='url(#f)'
                  xlinkHref='#e'
                />
              </g>
            </g>
          </svg>
        </div>
      </div>
    </header>
  )
}
