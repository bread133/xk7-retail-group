import React from 'react'

import { Header } from '@/components/header'
import { Hero } from '@/components/hero'
import { FileInput } from '@/components/file-input'
import { BorrowingTable } from '@/components/borrowing-table'

export default function Home() {
  return (
    <React.Fragment>
      <Header />
      <Hero />

      <div className='w-full flex justify-center items-center flex-col pb-24 space-y-16'>
        <FileInput />

        <BorrowingTable />
      </div>
    </React.Fragment>
  )
}
