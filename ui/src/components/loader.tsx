
interface Props { className?: string }
const Loader = (props: Props) => {
  return (
    <div className={`${props.className} flex w-full justify-center`}>
      <div className="w-12 h-12 border-4 border-transparent border-t-white rounded-full animate-spin" />
    </div>
  )
}

export default Loader
