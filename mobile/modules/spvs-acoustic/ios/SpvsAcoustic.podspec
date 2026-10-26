Pod::Spec.new do |s|
  s.name = 'SpvsAcoustic'
  s.version = '1.0.0'
  s.summary = 'Ephemeral foreground acoustic challenge capture'
  s.description = s.summary
  s.license = { :type => 'MIT' }
  s.author = 'SPVS'
  s.homepage = 'https://github.com/Anishpantham/Secure-Presence-Verification-System-SVPS---Attendance-Software'
  s.platforms = { :ios => '16.4' }
  s.source = { :git => s.homepage }
  s.static_framework = true
  s.dependency 'ExpoModulesCore'
  s.frameworks = 'AVFoundation'
  s.source_files = '**/*.{h,m,mm,swift}'
  s.swift_version = '5.9'
end
