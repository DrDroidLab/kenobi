import logo from '../../data/no-data-alert-icon.png';

const NoExistingMonitorTransaction = () => {
  return (
    <>
      <div className="justify-center w-full items-center flex flex-col py-8">
        <img src={logo} alt="logo" className="h-20 mb-4 " />
        <div className="text-sm text-gray-500 mb-2 text-center">No monitor transactions found</div>
      </div>
    </>
  );
};

export default NoExistingMonitorTransaction;
