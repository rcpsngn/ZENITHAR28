import React, { useState, useEffect } from 'react';
import { Routes, Route, Link, useLocation } from 'react-router-dom';
import { Users, Clock, DollarSign, Calendar } from 'lucide-react';
import { Button } from '../../components/ui/button';
import EmployeeList from './EmployeeList';
import AttendanceList from './AttendanceList';
import SalaryList from './SalaryList';
import LeaveList from './LeaveList';

const PersonnelPage = () => {
  const location = useLocation();
  
  const tabs = [
    { path: '/dashboard/personnel', label: 'Personeller', icon: Users },
    { path: '/dashboard/personnel/attendance', label: 'Giriş-Çıkış', icon: Clock },
    { path: '/dashboard/personnel/salaries', label: 'Maaşlar', icon: DollarSign },
    { path: '/dashboard/personnel/leaves', label: 'İzinler', icon: Calendar },
  ];

  return (
    <div data-testid="personnel-page">
      <div className="mb-6">
        <h1 className="text-3xl font-manrope font-bold text-slate-900 mb-2">
          Personel Yönetimi
        </h1>
        <p className="text-slate-600">
          Çalışanlarınızı yönetin, giriş-çıkış takibi yapın, maaş ve izinleri kontrol edin
        </p>
      </div>

      <div className="border-b border-slate-200 mb-6">
        <nav className="flex space-x-4">
          {tabs.map((tab) => {
            const isActive = location.pathname === tab.path;
            return (
              <Link
                key={tab.path}
                to={tab.path}
                data-testid={`tab-${tab.label.toLowerCase().replace(/\s/g, '-')}`}
              >
                <div className={`flex items-center gap-2 px-4 py-3 border-b-2 transition-colors ${
                  isActive 
                    ? 'border-primary text-primary font-bold' 
                    : 'border-transparent text-slate-600 hover:text-slate-900'
                }`}>
                  <tab.icon className="h-5 w-5" />
                  <span>{tab.label}</span>
                </div>
              </Link>
            );
          })}
        </nav>
      </div>

      <Routes>
        <Route path="/" element={<EmployeeList />} />
        <Route path="/attendance" element={<AttendanceList />} />
        <Route path="/salaries" element={<SalaryList />} />
        <Route path="/leaves" element={<LeaveList />} />
      </Routes>
    </div>
  );
};

export default PersonnelPage;
